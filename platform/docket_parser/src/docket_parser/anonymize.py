import itertools
import logging
import re
import time
from copy import copy
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Callable

import pikepdf
from faker import Faker
from pikepdf import Token, TokenFilter, TokenType, ContentStreamInstruction, ContentStreamInlineImage

from docket_parser import parse_pdf
from docket_parser.parsing import text_from_pdf
from .extraction import DocketReader, TextState
from .font import PdfFontWrapper

logger = logging.getLogger(__name__)
TEXT_SHOWING_OPERATORS = ("Tj", "TJ")
ContentStreamElement = ContentStreamInstruction | ContentStreamInlineImage
fake = Faker('en_US')
Faker.seed(time.time_ns())


def generate_TJ_instruction(content: str, width: int, font: PdfFontWrapper) -> ContentStreamInstruction:
    """Return a pikepdf TJ ContentStreamInstruction from the input.
    @param content: The unicode characters that the TJ instruction should have
    @param width: The total horizontal displacement, in glyph space units, that the instruction should have
    @param font: The PdfFontWrapper to use to calculate the actual instruction contents"""
    width_of_characters = font.get_unicode_string_width(content)
    # This may be negative
    width_to_add = width - width_of_characters
    if len(content) <= 1:
        content = ' '
        return ContentStreamInstruction([''], pikepdf.Operator("Tj"))
    space_between_chars = width_to_add // (len(content) - 1)
    space_remainder = width_to_add % (len(content) - 1)
    width_of_a_space = font.get_unicode_string_width(" ")

    # The resulting instruction must have the given width. There are multiple reasonable ways to make that happen.
    # If the unmodified width of the content (i.e. without any individual character spacing) is less than the required
    # width, we can:
    # 1. add all the necessary space at the end
    # 2. add all necessary space at the beginning
    # 3. If there are spaces (U+0020), add the necessary space after the spaces
    # 4. add an equal amount of space after every character
    # 5. add an equal amount of space after every character except the last one

    # There are other pdf commands we could use to stretch text, but those don't appear in these documents, so the
    # document reader is not built to process them.

    # When the unmodified width is greater than the given width, we can remove an equal amount of space after every
    # character except the last one.

    if space_between_chars > width_of_a_space / 3:
        logger.warning(f"Characters had to be severely squished for the text '{content}'")
    elif space_between_chars < -width_of_a_space / 2:
        logger.warning(f"Characters had to be severely spaced out for the text '{content}'")

    # This adds or removes an equal amount of space after every character except the last one
    inner_character_spaces = [-space_between_chars - (index < space_remainder) for index in range(len(content) - 1)]
    inner_character_spaces.append(0)

    bytestring = font.unicode_to_bytestring(content)
    zipped = zip(map(chr, bytestring), inner_character_spaces)
    operand = list(itertools.chain.from_iterable(zipped))

    # Check that the sum of added widths is equal to width_to_add
    assert (thesum := sum(filter(lambda x: isinstance(x, int), operand))) == -width_to_add, \
        f"{thesum=},{-width_to_add=}"

    return ContentStreamInstruction([operand], pikepdf.Operator("TJ"))


class TextShowingInstruction(ContentStreamInstruction):
    """For convenience, class that inherits from ContentStreamInstruction and also stores (unicode) content and width
    for text showing instructions."""

    def __init__(self, instruction: ContentStreamInstruction, content: str, width):
        super().__init__(instruction)
        self.content = content
        self.width = width


class TextSegment:
    """ Stores text segment properties.
    Attributes:
        content (str): The text contained in the segment
        font_name (str): Resource name of the font used for the segment
        content_with_instructions: List of dicts. only for Tj, TJ instructions, characters w/ corresponding content
            stream instruction index and position within that instruction's operands
        horizontal_displacement: TODO
    """

    # Text segment needs to know what the text output of each of its instructions is
    # Then the stored instruction needs to know and be able to change what parts
    # of operands correspond to specific characters
    # content: str = ''

    def __init__(self, font_getter: Callable[[], PdfFontWrapper]):
        self.font_getter = font_getter
        self._instructions = []
        self.text_instruction_contents = {}
        # self.content_with_instructions: list[dict] = []
        self.content = ''
        self.horizontal_displacement: float = 0.

    def reset(self):
        self.__init__(self.font_getter)

    def get_content(self) -> str:
        # return ''.join(d['char'] for d in self.content_with_instructions if 'char' in d)
        return self.content

    @property
    def font(self) -> PdfFontWrapper:
        return self.font_getter()

    # This commented out method uses a different strategy for replacements which leads to different results.
    # It does not mess with character spacing, and will throw an error if the replacement is too wide.
    # def replace(self, new_content: str):
    #     """Attempt to replace current content with new given content.
    #     Will throw error if doing the replacement would make any commands too wide"""
    #     original_width = self.font.get_unicode_string_width(self.get_content())
    #     new_width = self.font.get_unicode_string_width(new_content)
    #     # if original_width < new_width:
    #     #     raise ValueError(
    #     #         f"Replacement {new_content} for {self.get_content()} is too wide. {original_width} < {new_width}")
    #     remaining_content = new_content
    #     new_instructions = []
    #     for instruction in self._instructions:
    #         if not str(instruction.operator) in TEXT_SHOWING_OPERATORS:
    #             new_instructions.append(instruction)
    #             continue
    #         # Check if we have to modify the instruction
    #         if remaining_content.startswith(instruction.content):
    #             remaining_content = remaining_content[len(instruction.content):]
    #             new_instructions.append(instruction)
    #             continue
    #         # Find how many characters we can fit into the instruction, ignoring individual glyph spacing
    #         stop_index = 0
    #         substring_width = 0
    #         for index, char in enumerate(remaining_content):
    #             if (new_width := substring_width + self.font.get_unicode_string_width(
    #                     char)) > instruction.width:
    #                 stop_index = index
    #                 break
    #             substring_width = new_width
    #         else:
    #             stop_index = len(remaining_content)
    #         new_instruction_content = remaining_content[:stop_index]
    #         remaining_content = remaining_content[stop_index:]
    #         # new_instruction = instruction.get_instruction_with_new_content(new_instruction_content)
    #         # new_instruction = generate_TJ_instruction(new_instruction_content, new_width, self.font)
    #         new_instruction = generate_TJ_instruction(new_instruction_content, substring_width, self.font)
    #         new_instructions.append(new_instruction)
    #     self._instructions = new_instructions

    def replace(self, new_content: str):
        remaining_width = sum(instr.width for instr in self._instructions if isinstance(instr, TextShowingInstruction))
        remaining_content = new_content
        new_instructions = []
        for instruction in self._instructions:
            if not isinstance(instruction, TextShowingInstruction):
                new_instructions.append(instruction)
                continue

            # cur_instruction_content, _ = self.font.get_content_and_width()
            # Check if we have to modify the instruction
            if remaining_content.startswith(instruction.content):
                remaining_content = remaining_content[len(instruction.content):]
                new_instructions.append(instruction)
                remaining_width -= instruction.width
                continue
            # Shove all the remaining characters into the first instruction we need to modify.
            new_instruction_content = remaining_content
            remaining_content = ''
            new_instruction = generate_TJ_instruction(new_instruction_content, remaining_width, self.font)
            new_instructions.append(new_instruction)

        self._instructions = new_instructions

    def add_instruction(self, instruction: ContentStreamInstruction, text_state: TextState):
        """Add an instruction to this text segment. Use this method instead of directly modifying ._instructions"""
        operator = str(instruction.operator)
        if operator not in TEXT_SHOWING_OPERATORS:
            self._instructions.append(instruction)
            return
        elif operator == 'Tj':
            bytestring = bytes(instruction.operands[0])
            content, width = self.font.get_content_and_width(bytestring)
            displacement = width / 1000 * text_state.size
            self.horizontal_displacement += displacement
            self.content += content
            self._instructions.append(TextShowingInstruction(instruction, content, width))
        elif operator == 'TJ':
            for operand_index, operand in enumerate(instruction.operands[0]):
                if hasattr(operand, '__bytes__'):
                    bytestring = bytes(operand)
                    content, width = self.font.get_content_and_width(bytestring)
                    displacement = width / 1000 * text_state.size
                    self.horizontal_displacement += displacement
                    self.content += content
                else:
                    self.horizontal_displacement -= operand * text_state.size / 1000
            try:
                # noinspection PyUnboundLocalVariable
                self._instructions.append(TextShowingInstruction(instruction, content, width))
            except NameError as err:
                err.add_note(f"Failed to process TJ instruction: {instruction}")
                raise err


ReplacementType = str | Callable[[re.Match[str]], str]


class AnonymizingCSInstructionFilter:
    def __init__(self, fonts: dict[str, PdfFontWrapper],
                 sensitive_info_replacements: dict[str | re.Pattern, ReplacementType],
                 x_tolerance=.3, y_tolerance=1):
        self.fonts = fonts
        self.replacements_dict = sensitive_info_replacements
        self.x_tolerance = x_tolerance
        self.y_tolerance = y_tolerance
        # We don't care about font size, but it costs very little to keep track of it anyway if we ever needed.
        self.text_state = TextState('', 0)
        self.text_state_stack: list[TextState] = []
        self.cur_segment = TextSegment(self.get_font)
        self._filtered_content_stream = []

    def get_font(self) -> PdfFontWrapper:
        font_name = self.text_state.font_name
        return self.fonts[font_name]

    def filter_cs_instructions(self, parsed_content_stream: list[ContentStreamElement]) -> list[ContentStreamElement]:
        self._filtered_content_stream = []
        for instruction in parsed_content_stream:

            if isinstance(instruction, ContentStreamInlineImage):
                # these objects can appear in pikepdf parsed content streams, but we don't care about them.
                # Also, they cannot be inside a text block.
                self._filtered_content_stream.append(instruction)
                continue
            self.handle_instruction(instruction)

        return self._filtered_content_stream

    def handle_instruction(self, instruction: ContentStreamInstruction):
        self.cur_segment.add_instruction(instruction, copy(self.text_state))
        operator = str(instruction.operator)

        if operator == 'Tf':
            self.flush_cur_segment()
            font_name, font_size = instruction.operands
            self.text_state = TextState(str(font_name), float(font_size))
        elif operator == 'q':
            self.text_state_stack.append(self.text_state)
        elif operator == 'Q':
            self.flush_cur_segment()
            self.text_state = self.text_state_stack.pop()
        elif operator == 'ET':
            self.flush_cur_segment()
        elif operator == 'Td':
            x_translation, y_translation = (float(obj) for obj in instruction.operands)
            # flush segment unless moving to last shown character (within x tolerance)
            if abs(y_translation) <= self.y_tolerance and \
                    abs(x_translation - self.cur_segment.horizontal_displacement) < self.x_tolerance:
                self.cur_segment.horizontal_displacement = 0
            else:
                self.flush_cur_segment()

    def flush_cur_segment(self):
        original_content = self.cur_segment.get_content()
        new_content = original_content
        made_changes = False
        for pattern, replacement in self.replacements_dict.items():
            new_content, num_replacements = re.subn(pattern, replacement, new_content)
            made_changes |= num_replacements
        if made_changes:
            if any(pattern.search(new_content) for pattern in self.replacements_dict.keys()):
                raise ValueError(f"Made all the replacements, but final result still matches a pattern.\n"
                                 f"{original_content=}, {new_content=}")
            logger.debug(f"original: {original_content}\nreplaced: {new_content}")
            self.cur_segment.replace(new_content)
        self._filtered_content_stream += self.cur_segment._instructions
        self.cur_segment.reset()


class BackgroundColorCSInstructionFilter:
    def __init__(self, r: float, g: float, b: float):
        operands = [r, g, b]
        for intensity in operands:
            if 0 > intensity or intensity > 1:
                raise ValueError("Color intensities must be between 0.0 and 1.0")
        self.color_instruction = ContentStreamInstruction(operands, pikepdf.Operator('rg'))

    def filter_cs_instructions(self, parsed_content_stream: list[ContentStreamElement]) -> list[ContentStreamElement]:
        filtered_content_stream = parsed_content_stream[:1]
        rectangle_instruction = ContentStreamInstruction([0, 0, 612, -792], pikepdf.Operator('re'))
        fill_instruction = ContentStreamInstruction([], pikepdf.Operator('f'))
        filtered_content_stream += [self.color_instruction, rectangle_instruction, fill_instruction]
        filtered_content_stream += parsed_content_stream[1:]
        return filtered_content_stream


class ReadingTokenFilter(TokenFilter):
    """Token filter which stores all tokens from the content stream, while not making any changes to it."""

    def __init__(self):
        super().__init__()
        self.tokens = []

    def handle_token(self, token: Token = ...) -> None | list | Token:
        self.tokens.append(token)
        return token


class ReplacingTokenFilter(TokenFilter):
    """Token filter which ignores any incoming tokens, and just outputs the list of tokens it was initialized with."""

    def __init__(self, new_tokens: list[Token]):
        super().__init__()
        self.token_list = new_tokens

    def handle_token(self, token: Token = ...) -> None | list | Token:
        if token.type_ == TokenType.eof:
            return self.token_list


def tokens_from_cs(cs: bytes) -> list[Token]:
    """Input: a raw, uncompressed PDF content stream in bytes.
       Output: list of qpdf tokens.
       Uses pikepdf to apply qpdf's tokenizer to the content stream,
       breaking it down into individual units called tokens, and returns them as a list.
       It's convoluted because pikepdf doesn't directly expose qpdf's tokenizer"""
    new_pdf = pikepdf.new()
    new_pdf.add_blank_page()
    new_page = new_pdf.pages[0]
    new_page.contents_add(cs)
    reading_filter = ReadingTokenFilter()
    new_page.get_filtered_contents(reading_filter)
    new_pdf.close()
    return reading_filter.tokens


def load_replacements(replacements_filename: str | Path):
    with open(replacements_filename, 'r') as file:
        file_content = file.readlines()
    replacements_dict = {}
    for line in file_content:
        line = line.strip()
        string, replacement = line.split(';')
        replacements_dict[re.compile(string)] = replacement
    return replacements_dict


def make_auto_replacements(document_text: str, existing_replacements: dict) -> dict[re.Pattern, str]:
    # Docket number replacements have to be consistent across files...
    # TODO: make this catch OTNs, docket numbers, and DCNs and create appropriate replacements
    replacements = existing_replacements.copy()
    date_pattern = re.compile(r"\d{2}/\d{2}/\d{4}")
    long_number_pattern = re.compile(r"[0-9]{3}[\-0-9]{2,}")
    date_matches: list[re.Match[str]] = re.findall(date_pattern, document_text)
    long_number_matches = re.findall(long_number_pattern, document_text)
    for date_match in date_matches:
        if date_match.string in replacements:
            continue
        random_date: date = fake.date()
        random_date_string = random_date.strftime("%m/%d/%Y")
        replacements[date_match.string] = random_date_string
    for long_number_match in long_number_matches:
        if long_number_match.string in replacements:
            continue
        template = re.sub(r"\d", "#", long_number_match.string)
        randomized = fake.numerify(template)
        replacements[long_number_match.string] = randomized
    return replacements


def get_available_characters(filename_or_stream: str | Path | BinaryIO) -> dict[str, set[str]]:
    """Returns a dictionary, keys are fonts, and values are the characters which are available in the document.
    Assumes 1-byte character ids."""
    remaining_characters_dict: dict[str, set] = {'normal': set(chr(i) for i in range(256)),
                                                 'bold': set(chr(i) for i in range(256))}
    reader = DocketReader(filename_or_stream)
    page = reader.pages[0]
    font: PdfFontWrapper
    for name, font in page.fonts.items():
        key = page.font_output_names[name]
        chars = set(font.cid_to_unicode_map.values())
        remaining_characters_dict[key].intersection_update(chars)
    return remaining_characters_dict


def anonymize_pdf(filename_or_stream: str | Path | BinaryIO,
                  sensitive_info_replacements: dict[re.Pattern, str],
                  background_color: tuple[float] = (.85, 1, .92)) -> BytesIO:
    """param sensitive_info_replacements: dictionary, keys are compiled regex patterns and values are strings or
                                          functions that matches should be replaced with
    """
    parsed_info = parse_pdf(filename_or_stream)

    aliases = parsed_info.get("aliases", [])
    defendant_names = parsed_info.get("defendant_name").split(' ')
    sensitive_info = set(defendant_names)
    for name in aliases:
        name_without_commas = name.replace(',', '')
        sensitive_info.update(name_without_commas.split(' '))
    logger.debug(f'{sensitive_info=}')

    # regex = '|'.join(sensitive_info)
    # sensitive_info_pattern = re.compile(regex)

    reader = DocketReader(filename_or_stream)
    font_handler_list = [page.fonts for page in reader.pages]

    pdf = pikepdf.open(filename_or_stream)
    for index, page in enumerate(pdf.pages):
        # Abbreviating content stream to cs to avoid overly long variable names.
        cs_instructions = pikepdf.parse_content_stream(page)
        anonymizing_cs_filter = AnonymizingCSInstructionFilter(font_handler_list[index], sensitive_info_replacements)
        anonymized_cs_instructions = anonymizing_cs_filter.filter_cs_instructions(cs_instructions)
        # Add background color
        bg_color_cs_filter = BackgroundColorCSInstructionFilter(*background_color)
        anonymized_cs_instructions = bg_color_cs_filter.filter_cs_instructions(anonymized_cs_instructions)

        anonymized_cs = pikepdf.unparse_content_stream(anonymized_cs_instructions)
        anonymized_tokens = tokens_from_cs(anonymized_cs)
        replacing_filter = ReplacingTokenFilter(anonymized_tokens)
        page.add_content_token_filter(replacing_filter)
    buffer = BytesIO()
    pdf.save(buffer)
    buffer.seek(0)
    return buffer


def anonymize_pdfs(filenames_or_streams: list[str | Path | BinaryIO], replacement_file_paths: list[str | Path],
                   background_color=None):
    """Anonymize many pdfs at once, keeping replacements consistent across them."""
    if replacement_file_paths and len(filenames_or_streams) != len(replacement_file_paths):
        raise ValueError("The two lists passed must be the same length")
    shared_replacements = {}
    for filename_or_stream, replacement_file_path in zip(filenames_or_streams, replacement_file_paths):
        replacements_from_file = load_replacements(replacement_file_path)
        extracted_text = text_from_pdf(filename_or_stream)
        shared_replacements = make_auto_replacements(extracted_text, shared_replacements)
        if any([key in shared_replacements for key in replacements_from_file]):
            logger.warning("One or more replacements from file were overwritten")
        replacements = replacements_from_file.update(shared_replacements)
    # TODO: finish this function
