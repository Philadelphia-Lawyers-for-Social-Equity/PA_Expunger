import logging
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from re import escape
from typing import Union, IO, List, Dict, Tuple

from numpy import matmul
from pypdf import PdfReader, PageObject
from pypdf.errors import PdfReadError
from pypdf.generic import DictionaryObject

from .font import get_unicode_map, get_widths_dict

logger = logging.getLogger(__name__)


@dataclass()
class TextSegment:
    """ Stores text segment properties.
    Attributes:
        content (str): The text contained in the segment
        coordinates (tuple[float, float]): (x, y) coordinates of the point where segment started,
                                           in pdf user space units
        font_name (str): Shortened name of the font used for the segment
        x_transform (float): Sum of x transformation... #TODO explain better
        y_transform (float): Sum of y transformation... #TODO explain better
    """
    content: str = ''
    coordinates: tuple[float, float] = None
    font_name: str = None
    x_transform: float = 0
    y_transform: float = 0

    def reset(self):
        self.__init__()


@dataclass(frozen=True)
class TextState:
    """ Contains variables of pdf text state.
     Attributes:
         font_name (str): Font name
         size (float): Font size
         """
    font_name: str
    size: float


class DocketReader(PdfReader):
    """Subclass of pypdf PdfReader for reading dockets"""
    # These characters need to be ones that aren't in the pdf.
    # Maybe refactor these to not be class variables? Also, could dynamically change these to characters not in the pdf.
    terminator = '\n'
    tab = '_'
    comes_before = '|'
    properties_open = '['
    properties_close = ']'
    box_wrap = '^'

    def __init__(self, stream: Union[str, IO, Path]):
        super().__init__(stream)
        if self.metadata.get('/Creator') != 'Crystal Reports':
            # This warning should get passed along to person using our app (end user).
            logger.warning(f"{self.__class__.__name__} is only designed to read pdfs by Crystal Reports.\n"
                           f"Instead found: {self.metadata.get('/Producer')}, {self.metadata.get('/Creator')}")
        self.font_map_dicts = {}
        self._pages = [DocketPageObject(self, page) for page in super().pages]

    @property
    def pages(self) -> List['DocketPageObject']:
        return self._pages

    def visit(self, **kwargs) -> None:
        """Visits all pages. Passes arguments through to extract_text."""
        for page in self.pages:
            page.extract_text(**kwargs)

    def extract_text(self, debug_log_operations=False, **kwargs) -> str:
        kwargs["debug_log_operations"] = debug_log_operations
        extracted_text = ''
        for page in self.pages:
            extracted_text += page.extract_text(**kwargs)
        return extracted_text

    @classmethod
    def get_special_characters(cls) -> List[str]:
        """Return a list of each special character used by this reader."""
        return [cls.tab, cls.terminator, cls.properties_open, cls.properties_close, cls.comes_before, cls.box_wrap]

    @classmethod
    def generate_content_regex(cls) -> str:
        """Return a regular expression that will match any character that is not added by this reader."""
        # inserted_chars = cls.tab  + cls.properties_open + cls.properties_close + cls.comes_before
        inserted_chars = ''.join(cls.get_special_characters())
        inserted_chars_expression = '[^' + escape(inserted_chars) + ']'
        return inserted_chars_expression

    def _debug_get_all_operations(self) -> List[List[Union[bytes, List]]]:
        """For debugging purposes, collect and return a list of all operations in the pdf's content stream"""
        operations = []

        # noinspection PyUnusedLocal
        def visitor(operator, operand, cm, tm):
            operations.append([operator, operand])

        self.visit(visitor_operand_before=visitor)
        return operations

    def _debug_count_operators_used(self) -> Dict[bytes, int]:
        """For debugging purposes, collect all operators used in pdf and return dictionary with counts for each."""
        operator_counts = {}

        # noinspection PyUnusedLocal
        def visitor(operator, *args):
            if operator not in operator_counts:
                operator_counts[operator] = 1
            else:
                operator_counts[operator] += 1

        self.visit(visitor_operand_before=visitor)
        return operator_counts


class DocketPageObject(PageObject):
    """Subclass of pypdf's PageObject to give an extract_text method that is an improvement of pypdf's extract_text
    specifically for reading dockets.
    Info about pdfs: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
    Relevant sections referenced in comments. Text info overview: section 9.1"""

    def __init__(self, reader: DocketReader, page: PageObject) -> None:
        """Copy info from given page to self, and prepare font lookup dictionaries"""

        # noinspection PyTypeChecker
        super().__init__(pdf=reader, indirect_reference=page.indirect_reference)
        self.reader = reader
        self.update(page)

        # Set up font dictionaries. Assumes TrueType font with /ToUnicode, see 9.6
        self.font_unicode_maps: Dict[str, Dict[int, str]] = {}
        self.font_width_dicts: Dict[str, Dict[int, int]] = {}
        self.font_output_names: Dict[str, str] = {}
        fonts = self['/Resources']['/Font']

        if len(fonts) > 2:
            logger.warning("There are more than two fonts in this docket, which is unexpected.")

        for font_resource_name in fonts:
            # NB: iterating through fonts.items() would give indirect references instead of actual font objects
            font: DictionaryObject = fonts[font_resource_name]
            unicode_map = get_unicode_map(font)
            self.font_unicode_maps[font_resource_name] = unicode_map
            self.font_width_dicts[font_resource_name] = get_widths_dict(font)

            for char in unicode_map.values():
                if char in reader.get_special_characters():
                    raise PdfReadError(f"Special character '{char}' was found in pdf's fonts. "
                                       "Please use a different special character.")

            if 'bold' in font['/BaseFont'].lower():
                self.font_output_names[font_resource_name] = 'bold'
            else:
                self.font_output_names[font_resource_name] = 'normal'

    def get_content_and_width(self, font_name: str, bs: bytes) -> Tuple[str, int]:
        """Decode byte-string to unicode str and calculate horizontal width."""
        content = ''
        width = 0
        for character_id in bs:
            content += self.font_unicode_maps[font_name][character_id]
            width += self.font_width_dicts[font_name][character_id]
        return content, width

    @staticmethod
    def mult(tm: List[float], cm: List[float]) -> List[float]:
        """ Does matrix multiplication with the shortened forms of matrices tm, cm.
            See 9.4.2 Tm operator for description of shortened matrix
            """
        # If we don't want to use numpy, can instead copy the mult function from
        # pypdf._page.PageObject._extract_text
        mat1 = [[tm[0], tm[1], 0],
                [tm[2], tm[3], 0],
                [tm[4], tm[5], 1]]
        mat2 = [[cm[0], cm[1], 0],
                [cm[2], cm[3], 0],
                [cm[4], cm[5], 1]]
        result = matmul(mat1, mat2)
        return [result[0, 0], result[0, 1], result[1, 0], result[1, 1], result[2, 0], result[2, 1], result[2, 2]]

    def extract_text(self, x_tolerance=.3, y_tolerance=1, debug_log_operations=False, **kwargs) -> str:
        """ Extract text from a docket, with coordinates and font name.
        Text will be ordered as it is in pdf content stream. Text that is in the same block in pdf content stream, has
        the same font, and is on the same horizontal line will be considered a "segment".
        y_tolerance determines how much vertical space is required to count as a new segment.
        Spacing larger than x_tolerance that comes from pdf positioning instructions (not space characters) will be
        represented by the reader's tab character if positive, and the reader's comes_before character if negative.
        Each output segment will have x, y coordinates and font name at the end, surrounded by reader's properties_open
        and properties_close.
        Segments are separated by reader's terminator character.
        """

        # text state is a subset of graphics state, see 9.3.1
        text_state = TextState('', 0)
        text_state_stack: List[TextState] = []

        # segment will be modified until terminate_segment() is called,
        # which adds a copy of segment to the list, and resets segment
        segment = TextSegment()
        extracted_segments: List[TextSegment] = []

        # displacement calculation details in 9.4.4
        # cur_displacement stores how much horizontal space is taken up by text, in text units, since last repositioning
        # See handling for 'Td' operator for how/why this is used.
        cur_displacement: float = 0.0

        def terminate_segment() -> None:
            """End the current text segment, adding a copy to extracted_segments.
             Resets segment and cur_displacement"""
            nonlocal text_state, cur_displacement
            if segment.content != '':
                if segment.content[-1] == self.reader.box_wrap:
                    # Having this character at the end of a segment is irrelevant for our purposes.
                    segment.content = segment.content[:-1]
                segment.font_name = self.font_output_names[text_state.font_name]
                extracted_segments.append(copy(segment))
            segment.reset()
            cur_displacement = 0.0

        def operation_visitor(operator, args, cm, tm) -> None:
            """Visitor function to process all important text-related operations in pdf content stream.
            """
            nonlocal text_state, cur_displacement

            if operator in (b'TJ', b'Tj') and segment.coordinates is None:
                # We want the output coordinates to be where the segment started, not get updated by 'Td' operations
                m = self.mult(tm, cm)
                segment.coordinates = m[4], m[5]

            if operator == b'Tf':
                # Sets font and size
                # new segment on font change
                terminate_segment()
                font_name, font_size = args
                text_state = TextState(font_name, font_size)
            elif operator == b'q':
                # push to graphics state stack. See 8.4.2
                # text state is a subset of graphics state, see 9.3.1
                # font, font size are included in text state.
                text_state_stack.append(text_state)
            elif operator == b'Q':
                # pop from graphics state stack
                terminate_segment()
                text_state = text_state_stack.pop()
            elif operator == b'ET':
                # End text block. See 9.4.1
                terminate_segment()
            elif operator == b'Td':
                # Move text position
                x_transform, y_transform = args
                if y_transform < 0 and abs(x_transform + segment.x_transform) < x_tolerance:
                    # This happens when content of a left-justified text box(?) wraps to next line.
                    # Might happen in other situations that we don't care about?
                    # TODO: find example where a text box is interrupted by page break and handle it
                    segment.content += self.reader.box_wrap
                    segment.x_transform = 0
                    segment.y_transform += y_transform
                elif y_transform > 0 and abs(y_transform + segment.y_transform) < y_tolerance:
                    # This happens when text box ends and cursor goes back up to current line.
                    segment.y_transform = 0
                    segment.x_transform = 0
                    if x_transform < 0:
                        segment.content += self.reader.comes_before
                    else:
                        # could check spacing/overlap here, but probably not necessary
                        segment.content += self.reader.tab
                elif abs(y_transform) >= y_tolerance:
                    # Every case I've seen with +-<1 unit change is on the same logical line,
                    # but that might not always be true.
                    terminate_segment()
                elif x_transform < 0 and segment.content != '':
                    # Every time there's a negative x transform in dockets, it would be correct to prepend the following
                    # text to previous text instead of append. Could implement that, but inserting an unused character
                    # works for parsing.
                    segment.content += self.reader.comes_before
                elif x_transform > 0 and segment.content != '':
                    # Positive x transform means moving start of next text placement to the right of the *start* of
                    # the last one. It could be moving it right to the end of the last shown text, which would be
                    # no/irrelevant space, or it could move it past the end of last shown text, which would be
                    # meaningful spacing. We keep track of displacement of last shown text to determine this.
                    units_of_spacing = x_transform - cur_displacement
                    if units_of_spacing > x_tolerance * text_state.size:
                        segment.content += self.reader.tab
                        # for debugging x_tolerance value:
                        # logger.debug(segment.content + f'{{{units_of_spacing:.1f}>{text_state.size}*{x_tolerance:.1f}}}')
                    elif units_of_spacing < -.1:
                        # -.1 because < 0 catches float rounding errors.
                        logger.debug(f"Potentially overlapping text after: '{segment.content}'.")
                    else:
                        # This is for detecting newline in textbox vs segment termination
                        segment.x_transform += x_transform
                cur_displacement = 0

            elif operator == b'TJ':
                # args will have exactly one element: a list of alternating byte-strings and ints for individual spacing
                # See 9.4.3
                for item in args[0]:
                    if isinstance(item, bytes):
                        # add_bytes_to_segment(item)
                        content, width = self.get_content_and_width(text_state.font_name, item)
                        displacement = width / 1000 * text_state.size
                        cur_displacement += displacement
                        segment.content += content
                    else:
                        cur_displacement -= item * text_state.size / 1000
            elif operator == b'Tj':
                # args will have exactly one element, a bytes instance. See 9.4.3
                content, width = self.get_content_and_width(text_state.font_name, args[0])
                displacement = width / 1000 * text_state.size
                cur_displacement += displacement
                segment.content += content
            elif operator in (b"'", b'"'):
                # These are text showing operators that aren't used in dockets. If we find docket that does use them,
                # will have to implement to catch all text. See 9.4.3
                logger.warning(f"Found unexpected text showing operator: {operator}")
            elif operator in (b'Tc', b'Tw', b'Tz', b'TL', b'Ts', b'gs'):
                # These are operators affecting text state that aren't used in dockets.
                # If we find docket that does use them, will have to implement to calculate correct displacement.
                # See 9.3.1
                logger.warning(f"Found unexpected text spacing operator: {operator}")
            elif operator in (b'T*', b'TD'):
                # See 9.4.2
                logger.warning(f"Found unexpected text positioning operator: {operator}")

        operations = []

        def visitor(operator, args, cm, tm) -> None:
            """Visitor function that calls our visitor and also a visitor_operand_before if we were passed one."""
            operation_visitor(operator, args, cm, tm)
            if kwargs.get('visitor_operand_before') is not None:
                kwargs['visitor_operand_before'](operator, args, cm, tm)
            if debug_log_operations:
                if operator == b'Tj':
                    content, width = self.get_content_and_width(text_state.font_name, args[0])
                    operations.append([operator, content])
                elif operator == b'TJ':
                    for item in args[0]:
                        if isinstance(item, bytes):
                            content, width = self.get_content_and_width(text_state.font_name, item)
                            operations.append([operator, content])
                else:
                    operations.append([operator, args])

        # avoid infinite recursion
        super_kwargs = copy(kwargs)
        super_kwargs['visitor_operand_before'] = visitor
        super().extract_text(**super_kwargs)

        if debug_log_operations:
            for operator, operand in operations:
                logger.debug(f"{operator}: {operand}")

        formatted_segments = [self.segment_to_str(seg) for seg in extracted_segments]
        return ''.join(formatted_segments)

    def segment_to_str(self, segment: TextSegment) -> str:
        """Take a TextSegment and return the content of segment plus formatted expression of its properties.
        Terminates with terminator character from reader."""
        rounded_coordinates = (round(coordinate, 2) for coordinate in segment.coordinates)
        # The grammar currently expects this exact format, so it will need to change if this does.
        properties = ''.join(f'{n:06.2f},' for n in rounded_coordinates)
        properties += segment.font_name
        properties = self.reader.properties_open + properties + self.reader.properties_close
        segment_as_string = segment.content + properties + self.reader.terminator
        return segment_as_string
