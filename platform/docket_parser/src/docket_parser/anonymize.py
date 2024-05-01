import itertools
import json
import logging
import random
import re
import string
import time
from copy import copy
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Callable, SupportsBytes, SupportsInt, Any

import pikepdf
from faker import Faker
from pikepdf import ContentStreamInstruction, ContentStreamInlineImage

from docket_parser.parsing import text_from_pdf, parse_extracted_text
from .extraction import DocketReader, TextState
from .font import PdfFontWrapper

logger = logging.getLogger(__name__)
TEXT_SHOWING_OPERATORS = ("Tj", "TJ")
ContentStreamElement = ContentStreamInstruction | ContentStreamInlineImage
fake = Faker('en_US')
Faker.seed(time.time_ns())


def generate_TJ_instruction(content: str, width: int, font: PdfFontWrapper) -> tuple[ContentStreamInstruction, str]:
    """Return a pikepdf TJ ContentStreamInstruction from the input, and a string containing any warnings
    @param content: The unicode characters that the TJ instruction should have
    @param width: The total horizontal displacement, in glyph space units, that the instruction should have
    @param font: The PdfFontWrapper to use to calculate the actual instruction contents"""
    warning_text = ""
    try:
        width_of_characters = font.get_unicode_string_width(content)
    except KeyError as err:
        err.add_note(f"The font with base name {font['/BaseFont']} does not contain the specified character. "
                     f"Available characters in the font are:\n{''.join(font.get_unicode_characters())}")
        raise err
    # This may be negative
    width_to_add = width - width_of_characters
    if len(content) <= 1:
        return ContentStreamInstruction([''], pikepdf.Operator("Tj")), warning_text
    extra_space_between_chars = width_to_add // (len(content) - 1)
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

    # These warning limits are subjective
    if extra_space_between_chars > width_of_a_space / 3:
        warning_text = f"characters had to be severely spaced out"
    elif extra_space_between_chars < -width_of_a_space / 4:
        warning_text = f"characters had to be severely squished"

    # This adds or removes an equal-ish amount of space after every character except the last one
    inner_character_spaces = [-extra_space_between_chars - (index < space_remainder) for index in
                              range(len(content) - 1)]
    inner_character_spaces.append(0)

    bytestring = font.unicode_to_bytestring(content)
    zipped = zip(map(chr, bytestring), inner_character_spaces)
    operand = list(itertools.chain.from_iterable(zipped))

    # Check that the sum of added widths is equal to width_to_add
    width_is_correct = (the_sum := sum(filter(lambda x: isinstance(x, int), operand))) == -width_to_add
    assert width_is_correct, f"{the_sum=}, {-width_to_add=}"

    return ContentStreamInstruction([operand], pikepdf.Operator("TJ")), warning_text


class TextShowingInstruction(ContentStreamInstruction):
    """For convenience, class that inherits from ContentStreamInstruction and also stores (unicode) content and width
    (in glyph space units) for text showing instructions."""

    def __init__(self, instruction: ContentStreamInstruction, content: str, width: int):
        super().__init__(instruction)
        self.content = content
        self.width = width


class TextSegment:
    """ Stores text segment properties.
    Attributes:
        content (str): The text contained in the segment
        font_getter: Function which retrieves the font
        horizontal_displacement: Used only while building the segment, to keep track of horizontal displacement in user
                                 space units since the last translation instruction.
    """

    def __init__(self, font_getter: Callable[[], PdfFontWrapper]):
        """Initialize the text segment.
           font_getter must be a callable with no arguments which returns a PdfFontWrapper."""
        self.font_getter = font_getter
        self._instructions = []
        self.content = ''
        self.horizontal_displacement: float = 0.

    def reset(self):
        self.__init__(self.font_getter)

    def get_content(self) -> str:
        return self.content

    @property
    def font(self) -> PdfFontWrapper:
        return self.font_getter()

    def replace(self, new_content: str):
        """Changes the instructions in this segment to replace the segment's content with the given content."""
        remaining_width = sum(instr.width for instr in self._instructions if isinstance(instr, TextShowingInstruction))
        remaining_content = new_content
        new_instructions = remaining_instructions = []
        for index, instruction in enumerate(self._instructions):
            if not isinstance(instruction, TextShowingInstruction):
                new_instructions.append(instruction)
                continue

            # Check if we have to modify the instruction
            if remaining_content.startswith(instruction.content):
                remaining_content = remaining_content[len(instruction.content):]
                new_instructions.append(instruction)
                remaining_width -= instruction.width
                continue
            # Shove all the remaining characters into the first instruction we need to modify.
            new_instruction_content = remaining_content
            new_instruction, warning_text = generate_TJ_instruction(new_instruction_content, remaining_width, self.font)
            new_instructions.append(new_instruction)

            if warning_text:
                content_before = ''.join(
                    instr.content for instr in self._instructions[index:] if isinstance(instr, TextShowingInstruction))
                logger.warning(f"When replacing \"{content_before}\" with \"{new_instruction_content}\","
                               f" {warning_text}.")
            remaining_instructions = self._instructions[index+1:]
            break

        text_displacement = [0., 0.]

        # Filter out any remaining text showing instructions or text displacement instructions, while keeping track of
        # the overall effect of Td instructions so that we can add one at the end.
        def filter_fn(instr: pikepdf.ContentStreamInstruction) -> bool:
            if str(instr.operator) == "Td":
                text_displacement[0] += float(instr.operands[0])
                text_displacement[1] += float(instr.operands[1])
                return False
            return not isinstance(instr, TextShowingInstruction)

        filtered_remaining_instructions = list(filter(filter_fn, remaining_instructions))

        if text_displacement != [0., 0.]:
            final_Td_instruction = ContentStreamInstruction(text_displacement, pikepdf.Operator("Td"))
            if filtered_remaining_instructions and str(filtered_remaining_instructions[-1].operator) == "ET":
                filtered_remaining_instructions.insert(-1, final_Td_instruction)
            else:
                filtered_remaining_instructions.append(final_Td_instruction)

        new_instructions.extend(filtered_remaining_instructions)
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
            instruction_content = ''
            instruction_width = 0
            for operand in instruction.operands[0]:
                if isinstance(operand, SupportsBytes):
                    bytestring = bytes(operand)
                    content, width = self.font.get_content_and_width(bytestring)
                    instruction_width += width
                    instruction_content += content
                elif isinstance(operand, SupportsInt):
                    instruction_width -= int(operand)
                else:
                    raise TypeError(f"Unexpected operand type in TJ instruction: {operand}")
            try:
                # noinspection PyUnboundLocalVariable
                self._instructions.append(TextShowingInstruction(instruction, instruction_content, instruction_width))
            except NameError as err:
                err.add_note(f"Failed to process TJ instruction: {instruction}")
                raise err
            self.content += instruction_content
            self.horizontal_displacement += instruction_width / 1000 * text_state.size


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
        content_before = content_after = original_content
        made_changes = False
        replacement_steps = []
        for pattern, replacement in self.replacements_dict.items():
            content_after, num_replacements = re.subn(pattern, replacement, content_before)
            if num_replacements:
                replacement_steps.append(
                    {"pattern matched": pattern, "replacement str or function": replacement, "from": content_before,
                     "to": content_after})
            content_before = content_after
            made_changes |= num_replacements
        if replacement_steps:
            if matching_patterns := list(pattern for pattern in self.replacements_dict.keys() if pattern.search(content_after)):
                error_message = (f"Made all the replacements, but final result still matches a pattern.\n"
                                 f"{original_content=}, {content_after=}, pattern(s) still matched={matching_patterns}\n"
                                 f"Replacement steps: {json.dumps(replacement_steps, indent=2, default=str)}")
                raise ValueError(error_message)
            logger.debug(f"Replacement steps: {json.dumps(replacement_steps, indent=2, default=str)}")
            self.cur_segment.replace(content_after)
        self._filtered_content_stream += self.cur_segment._instructions
        self.cur_segment.reset()


def generate_background_color_changing_instructions(r: float, g: float, b: float, width: float, height: float):
    """r, g, b are floats between 0 and 1, corresponding to the intensities of red, green, and blue respectively"""
    if not (0 <= r <= 1 and 0 <= g <= 1 and 0 <= b <= 1):
        raise ValueError("Color intensities must be between 0.0 and 1.0")
    color_intensities = [r, g, b]
    rectangle_coordinates = [0, 0, width, height]
    return [
        ContentStreamInstruction([], pikepdf.Operator('q')),                      # Save graphics state
        ContentStreamInstruction(color_intensities, pikepdf.Operator('rg')),      # set non-stroking color
        ContentStreamInstruction(rectangle_coordinates, pikepdf.Operator('re')),  # Add rectangle to path
        ContentStreamInstruction([], pikepdf.Operator('f')),                      # Fill the rectangle
        ContentStreamInstruction([], pikepdf.Operator('Q'))                       # Restore graphics state
    ]


def load_replacements(replacements_filename: str | Path):
    with open(replacements_filename, 'r') as file:
        file_content = file.readlines()
    replacements_dict = {}
    for line in file_content:
        # Allow comments starting with #
        if line.startswith("#") or line.isspace():
            continue
        line = line.strip()
        pattern_string, replacement = line.split(';')
        replacements_dict[re.compile(pattern_string)] = replacement
    return replacements_dict


def matches_any_pattern(string: str, replacements_dict: dict) -> bool:
    """Check if the string matches any of the patterns in replacements_dict's keys"""
    return any(pattern.search(string) for pattern in replacements_dict.keys())


def make_number_replacements(document_text: str, existing_replacements: dict,
                             available_characters: dict[str: set[str]]) -> dict[re.Pattern, str]:
    # Replacements have to be consistent across files
    replacements = existing_replacements.copy()

    # get number lists that can be used for replacements
    available_numbers = set(string.digits) & available_characters['normal']
    numbers = list(available_numbers)
    available_bold_numbers = set(string.digits) & available_characters['bold']
    bold_numbers = list(available_bold_numbers)

    # OTN
    OTN_pattern = re.compile(r"[A-Z][ ][0-9]{6}-[0-9]{1}")
    OTN_matches = re.findall(OTN_pattern, document_text)

    chars_for_OTN = [char for char in available_characters['normal'] if char in string.ascii_uppercase]
    for OTN_match in OTN_matches:
        if OTN_match in replacements:
            continue
        template = re.sub(r"[0-9]", "#", OTN_match[2:])
        pattern_conflicts = True
        while pattern_conflicts:
            randomized = random.choice(chars_for_OTN) + ' ' + fake.numerify(template)
            for char in randomized:
                if char.isnumeric() and (char not in numbers):
                    randomized = randomized.replace(char, random.choice(numbers))
            pattern_conflicts = matches_any_pattern(randomized, replacements)
        replacements[re.compile(OTN_match)] = randomized

    # Docket Number
    docket_num_pattern = re.compile(r"-[0-9]{7}-[0-9]{4}")
    docket_num_matches = re.findall(docket_num_pattern, document_text)

    # Find numbers used in bold font for use in docket number generation
    for docket_num_match in docket_num_matches:
        if docket_num_match in replacements:
            continue
        template = re.sub(r"[0-9]", "#", docket_num_match)
        randomized = make_random_number(template, bold_numbers, replacements)
        # create replacement for full docket number
        replacements[re.compile(docket_num_match)] = randomized
        # create replacement for docket number section when used in other numbers
        replacements[re.compile(docket_num_match[1:8])] = randomized[1:8]

    # Legacy Docket Numbers
    legacy_docket_pattern = re.compile(r"[A-Z][0-9]{10}")
    legacy_docket_matches = re.findall(legacy_docket_pattern, document_text)

    for legacy_docket_match in legacy_docket_matches:
        if legacy_docket_match in replacements:
            continue
        template = re.sub(r"[0-9]", "#", legacy_docket_match)
        randomized = make_random_number(template, numbers, replacements)
        replacements[re.compile(legacy_docket_match)] = randomized

    # Payment Plan and Receipt Numbers
    payment_plan_pattern = re.compile(r"-[0-9]{4}-[P,R][0-9]{9}")
    payment_plan_matches = re.findall(payment_plan_pattern, document_text)

    for payment_plan_match in payment_plan_matches:
        if payment_plan_match in replacements:
            continue
        template = re.sub(r"[0-9]", "#", payment_plan_match)
        randomized = make_random_number(template, numbers, replacements)
        replacements[re.compile(payment_plan_match)] = randomized

    # Long numbers (PA Driver's License Numbers, Legacy Microfilm Numbers, Related Docket Number,
    # District Control Numbers (DCNs), Police Incident Numbers)
    long_number_pattern = re.compile(r"(?<!\-)[0-9]{7,10}")
    long_number_matches = re.findall(long_number_pattern, document_text)

    for long_number_match in long_number_matches:
        if long_number_match in replacements:
            continue
        template = re.sub(r"[0-9]", "#", long_number_match)
        randomized = make_random_number(template, numbers, replacements)
        replacements[re.compile(long_number_match)] = randomized

    return replacements


def make_random_number(template: str, numbers: list, replacements: dict) -> str:
    pattern_conflicts = True
    while pattern_conflicts:
        randomized = fake.numerify(template)
        for char in randomized:
            if char.isnumeric() and (char not in numbers):
                randomized = randomized.replace(char, random.choice(numbers))
            pattern_conflicts = matches_any_pattern(randomized, replacements)
    return randomized


def find_date_patterns(document_text: str) -> (list[datetime], list[datetime]):
    long_date_pattern = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{4}")
    long_date_matches: list[re.Match[str]] = list(set(re.findall(long_date_pattern, document_text)))
    long_dates = [datetime.strptime(date, "%m/%d/%Y") for date in long_date_matches]

    short_date_pattern = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{2}(?![0-9])")
    short_date_matches: list[re.Match[str]] = re.findall(short_date_pattern, document_text)
    short_dates = [datetime.strptime(date, "%m/%d/%y") for date in short_date_matches]

    return long_dates, short_dates


def make_date_replacements(long_dates: list[str], short_dates: list[str],
                           existing_replacements: dict) -> (dict[re.Pattern, str], dict[re.Pattern, str]):
    dates = long_dates + short_dates
    dates.sort()
    random_dates = []
    long_date_replacements = {}
    short_date_replacements = {}
    start_date = datetime.strptime("01/01/1900", "%m/%d/%Y")
    end_date = datetime.strptime("12/31/2000", "%m/%d/%Y")

    for _ in range(len(dates)):
        new_random_date = fake.date_between(start_date=start_date, end_date=end_date)
        long_date_string = new_random_date.strftime("%m/%d/%Y")
        short_date_string = new_random_date.strftime("%m/%d/%y")
        while (long_date_string in long_dates) or matches_any_pattern(long_date_string, existing_replacements):
            new_random_date = fake.date_between(start_date=start_date, end_date=end_date)
            long_date_string = new_random_date.strftime("%m/%d/%Y")
        while (short_date_string in short_dates) or matches_any_pattern(short_date_string, existing_replacements):
            new_random_date = fake.date_between(start_date=start_date, end_date=end_date)
            short_date_string = new_random_date.strftime("%m/%d/%y")
        random_dates.append(new_random_date)
    random_dates.sort()

    for i, found_date in enumerate(dates):
        if found_date in long_dates:
            date_str = found_date.strftime("%m/%d/%Y")
            if re.compile(date_str) in existing_replacements:
                continue
            long_date_replacements[re.compile(date_str)] = random_dates[i].strftime('%m/%d/%Y')
        if found_date in short_dates:
            date_str = found_date.strftime("%m/%d/%y")
            if re.compile(date_str) in existing_replacements:
                continue
            short_date_replacements[re.compile(date_str)] = random_dates[i].strftime('%m/%d/%y')

    return long_date_replacements, short_date_replacements


def find_sensitive_info(document_text: str) -> set[str]:
    parsed_info = parse_extracted_text(document_text)

    aliases = parsed_info.get("aliases", [])
    defendant_names = parsed_info.get("defendant_name").split(' ')
    sensitive_info = set(defendant_names)
    for name in aliases:
        name_without_commas = name.replace(',', '')
        sensitive_info.update(name_without_commas.split(' '))
    return sensitive_info


def make_name_replacements(sensitive_info: set[str], existing_replacements: dict,
                           available_characters: dict[str: set[str]],
                           name_replacement_prompt: bool = False) -> dict[re.Pattern, str]:
    replacements = existing_replacements.copy()
    available_characters_both_fonts = available_characters['bold'] & available_characters['normal']
    available_uppercase_letters = set(string.ascii_uppercase) & available_characters_both_fonts
    uppercase_letters = list(available_uppercase_letters)
    uppercase_letters.sort()

    available_lowercase_letters = set(string.ascii_lowercase) & available_characters_both_fonts
    lowercase_letters = list(available_lowercase_letters)
    lowercase_letters.sort()

    # separate any names that are initials with periods
    name_initials = [info for info in sensitive_info if '.' in info]
    names = [info for info in sensitive_info if info not in name_initials]

    name_replacements = {}

    # Replace defendant names with user inputs
    # Replacement names entered into CLI will take priority over names in replacements file
    if name_replacement_prompt:
        if [name for name in names if re.compile(name) in replacements.keys()]:
            logger.warning("One or more defendant names found in replacement file, "
                           "and will be overwritten by replacements entered here")
        names_to_replace = list(sensitive_info)
        print(f"Create replacements for {sensitive_info} using these characters:\n"
              f"Uppercase Letters: {uppercase_letters}\n"
              f"Lowercase Letters: {lowercase_letters}")
        print(f"Type 'exit' to cancel name replacement and use auto-generated name values")
        name_count = 0
        while name_count < len(sensitive_info):
            name = names_to_replace[name_count]
            replacement_from_stdin = input(
                f"Enter a replacement for {name} (the name should be {len(name)} characters long)\n>")
            incompatible_characters = []
            if replacement_from_stdin == 'exit':
                confirm_stdin = input(f"Are you sure you want to cancel the name replacement? (y/n): ")
                if confirm_stdin.lower() == 'y':
                    name_replacement_prompt = False
                    break
                else:
                    continue
            else:
                for char in replacement_from_stdin:
                    if char in string.ascii_uppercase and char not in uppercase_letters:
                        incompatible_characters.append(char)
                    elif char in string.ascii_lowercase and char not in lowercase_letters:
                        incompatible_characters.append(char)
            if incompatible_characters:
                print(f"Error: {list(set(incompatible_characters))} cannot be used in the replacement name")
            else:
                if '.' in name:
                    name_replacements[re.compile(re.escape(name))] = replacement_from_stdin
                else:
                    name_replacements[re.compile(re.escape(name), re.IGNORECASE)] = replacement_from_stdin
                name_count += 1
        if name_replacement_prompt:
            name_replacements.update(replacements)

    # Replace names with randomly generated strings. Strings are limited to letters available in the parsed pdf's bold font
    # If one of the defendant's names is found in the replacement file, names will not be auto-generated
    if not name_replacement_prompt:
        if any(re.compile(name) in replacements.keys() for name in names):
            return replacements
        for initial in name_initials:
            randomized = make_random_name(uppercase_letters, lowercase_letters, len(initial)-2, ['.'])
            while (randomized in name_initials) or matches_any_pattern(randomized, replacements):
                randomized = make_random_name(uppercase_letters, lowercase_letters, len(initial)-2, ['.'])
            name_replacements[re.compile(re.escape(initial))] = randomized
        for name in names:
            randomized = make_random_name(uppercase_letters, lowercase_letters, len(name)-1)
            while matches_any_pattern(randomized, replacements):
                randomized = make_random_name(uppercase_letters, lowercase_letters, len(name)-1)
            name_replacements[re.compile(name, re.IGNORECASE)] = randomized
        replacements.update(name_replacements)

    return name_replacements if name_replacement_prompt else replacements


def make_random_name(uppercase_letters: list, lowercase_letters: list, name_length: int, initial: tuple = ('',)) -> str:
    first_letter = random.choices(uppercase_letters, k=1)
    next_letters = random.choices(lowercase_letters, k=name_length)
    initial = list(initial)
    return ''.join(first_letter + next_letters + initial)


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
        chars = set(font.get_unicode_characters())
        remaining_characters_dict[key].intersection_update(chars)
    return remaining_characters_dict


def anonymize_pdf(pdf_filename_or_stream: str | Path | BinaryIO,
                  sensitive_info_replacements: dict[re.Pattern, Any] | Path | str,
                  background_color: tuple[float, float, float] = (.85, 1, .92)) -> BytesIO:
    """param pdf_filename_or_stream: The filename or stream which contains the pdf to be anonymized.
    param sensitive_info_replacements: dictionary or file name. If dictionary, keys are compiled regex patterns and
                                       values are strings or functions that matches should be replaced with.
                                       If it's a file name, replacements will be loaded from it using load_replacements
    """
    if not isinstance(sensitive_info_replacements, dict):
        sensitive_info_replacements = load_replacements(sensitive_info_replacements)

    reader = DocketReader(pdf_filename_or_stream)
    font_handler_dict = reader.pages[0].fonts

    pdf = pikepdf.open(pdf_filename_or_stream)
    for index, page in enumerate(pdf.pages):
        # Abbreviating content stream to cs to avoid overly long variable names.
        media_box = page.MediaBox  # Get the media box of the page
        width = float(media_box[2] - media_box[0])
        height = float(media_box[3] - media_box[1])
        cs_instructions = pikepdf.parse_content_stream(page)
        bg_color_instructions = generate_background_color_changing_instructions(*background_color, width, height)
        color_changed_cs_instructions = bg_color_instructions + cs_instructions
        anonymizing_cs_filter = AnonymizingCSInstructionFilter(font_handler_dict, sensitive_info_replacements)
        try:
            anonymized_cs_instructions = anonymizing_cs_filter.filter_cs_instructions(color_changed_cs_instructions)
        except ValueError as err:
            err.add_note(f"Error occurred while anonymizing {pdf_filename_or_stream}")
            raise err

        binary_anonymized_cs = pikepdf.unparse_content_stream(anonymized_cs_instructions)
        page.Contents = pdf.make_stream(binary_anonymized_cs)
    buffer = BytesIO()
    pdf.save(buffer)
    buffer.seek(0)
    return buffer


def anonymize_pdfs(filenames_or_streams: list[str | Path | BinaryIO], replacement_file_paths: list[str | Path],
                   name_replacement_prompt: bool = False, background_color=(.85, 1, .92)) -> list[BytesIO]:
    """Anonymize many pdfs at once, keeping replacements consistent across them."""
    if replacement_file_paths and len(filenames_or_streams) != len(replacement_file_paths):
        raise ValueError("The two lists passed must be the same length")

    # Get available characters for use in auto-generation of docket numbers, defendant names, and OTNs
    available_characters = {'normal': set(), 'bold': set()}
    for filename_or_stream in zip(filenames_or_streams):
        new_characters = get_available_characters(filename_or_stream[0])
        new_bold_characters = new_characters['bold']
        new_normal_characters = new_characters['normal']
        if len(available_characters['bold']) > 0:
            available_characters['bold'] = available_characters['bold'].intersection(new_bold_characters)
        else:
            available_characters['bold'] = new_bold_characters
        if len(available_characters['normal']) > 0:
            available_characters['normal'] = available_characters['normal'].intersection(new_normal_characters)
        else:
            available_characters['normal'] = new_normal_characters

    replacements = {}
    long_dates = []
    short_dates = []
    sensitive_info = set()
    for filename_or_stream, replacement_file_path in zip(filenames_or_streams, replacement_file_paths):
        # get replacements from .anonymize file
        replacements_from_file = load_replacements(replacement_file_path)
        replacements.update(replacements_from_file)
        # create autoreplacements
        extracted_text = text_from_pdf(filename_or_stream)
        auto_replacements = make_number_replacements(extracted_text, replacements, available_characters)
        replacements.update(auto_replacements)
        # find date patterns
        new_long_dates, new_short_dates = find_date_patterns(extracted_text)
        long_dates = list(set(long_dates + new_long_dates))
        short_dates = list(set(short_dates + new_short_dates))
        # find names
        new_sensitive_info = find_sensitive_info(extracted_text)
        sensitive_info.update(new_sensitive_info)

    # create date replacements
    long_date_replacements, short_date_replacements = make_date_replacements(long_dates, short_dates, replacements)
    replacements.update(long_date_replacements)
    replacements.update(short_date_replacements)
    # add name replacements
    replacements = make_name_replacements(sensitive_info, replacements, available_characters, name_replacement_prompt)

    # make replacements in files
    anonymized_files = []
    for filename_or_stream in zip(filenames_or_streams):
        anonymized_file = anonymize_pdf(filename_or_stream[0], replacements, background_color)
        anonymized_files.append(anonymized_file)
    return anonymized_files
