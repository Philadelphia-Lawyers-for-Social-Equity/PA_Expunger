import logging
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from re import escape
from typing import Union, IO, List, Dict, Tuple

from numpy import matmul
from pypdf import PdfReader, PageObject
from pypdf._cmap import parse_to_unicode

logger = logging.getLogger(__name__)

@dataclass()
class TextSegment:
    """ Stores content of a text segment as well as coordinates in user space units and font name. """
    content: str = ''
    coordinates: tuple[float, float] = None
    font_name: str = None

    def reset(self):
        self.__init__()

@dataclass(frozen=True)
class TextState:
    """ Contains variables of pdf text state.
     Attributes:
         f_name (str): Font name
         size (float): Font size
         """
    f_name: str
    size: float

class DocketReader(PdfReader):
    """Subclass of pypdf PdfReader for reading dockets"""
    # These characters need to be ones that aren't in the pdf.
    # These also can't be whitespace unless we find a way to escape them when put into grammar
    newline = '^'
    tab = '_'
    comes_before = '|'
    properties_open = '['
    properties_close = ']'

    def __init__(self, stream: Union[str, IO, Path]):
        super().__init__(stream)
        self.font_map_dicts = {}
        self._pages = [DocketPageObject(self, page) for page in super().pages]

    @property
    def pages(self) -> List['DocketPageObject']:
        return self._pages

    def visit(self, **kwargs) -> None:
        """Visits all pages. Passes arguments through to extract_text."""
        for page in self.pages:
            page.extract_text(**kwargs)

    def extract_text(self, **kwargs) -> str:
        extracted_text = ''
        for page in self.pages:
            extracted_text += page.extract_text(**kwargs)
        return extracted_text

    @classmethod
    def generate_content_regex(cls) -> str:
        """Return a regular expression that will match any character that is not added by this reader."""
        # inserted_chars = cls.tab  + cls.properties_open + cls.properties_close + cls.comes_before
        inserted_chars = cls.tab + cls.newline + cls.properties_open + cls.properties_close + cls.comes_before
        inserted_chars_expression = '[^' + escape(inserted_chars) + ']'
        return inserted_chars_expression

    def _debug_get_all_operations(self) -> List[List[Union[bytes, List]]]:
        operations = []
        # noinspection PyUnusedLocal
        def visitor(operator, operand, cm, tm):
            operations.append([operator, operand])
        self.visit(visitor_operand_before=visitor)
        return operations

    def _debug_count_operators_used(self) -> Dict[bytes, int]:
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
    Relevant sections referenced in comments. 9.1"""


    def __init__(self, reader: DocketReader, page: PageObject) -> None:
        """Copy info from given page to self, and prepare font lookup dictionaries"""
        
        # noinspection PyTypeChecker
        super().__init__(pdf=reader, indirect_reference=page.indirect_reference)
        self.reader = reader
        self.update(page)
        
        # Set up font dictionaries. Assumes TrueType font with /ToUnicode, see 9.6
        self.font_map_dicts: Dict[str, Dict[str, str]] = {}
        self.font_width_dicts: Dict[str, Dict[str, int]] = {}
        self.font_output_names: Dict[str, str] = {}
        fonts = self['/Resources']['/Font']

        if len(fonts) > 2:
            logger.warning("There are more than two fonts in this docket, which is unexpected.")

        for font_resource_name in fonts:
            font_dict = fonts[font_resource_name]
            map_dict, space_code, int_entry = parse_to_unicode(font_dict, 0)
            self.font_map_dicts[font_resource_name] = map_dict

            widths_dict = {}
            for i in range(font_dict['/FirstChar'], font_dict['/LastChar']+1):
                char = chr(i)
                if char in map_dict:
                    widths_dict[chr(i)] = font_dict['/Widths'][i - font_dict['/FirstChar']]
            self.font_width_dicts[font_resource_name] = widths_dict

            if 'bold' in font_dict['/BaseFont'].lower():
                self.font_output_names[font_resource_name] = 'bold'
            else:
                self.font_output_names[font_resource_name] = 'normal'


    def extract_text(self, space_threshold=.3, **kwargs) -> str:
        """ Extract text from a docket, with coordinates and font name.
        Text will be ordered as it is in pdf content stream. Text that is in the same block in pdf content stream
        and on the same horizontal line will get output together. Spacing that comes from pdf instructions and not
        actual space characters will be represented by the reader's tab character if it's positive, and the reader's
        comes_before character if negative. Each output segment will have x, y coordinates and font name at the end,
        surrounded by reader's properties_open and properties_close.
        """

        text_state = TextState('', 0)
        segment = TextSegment()
        extracted_segments: List[TextSegment] = []
        text_state_stack: List[TextState] = []

        # displacement calculation details in 9.4.4
        # cur_displacement stores how much horizontal space is taken up by text, in text units, since last repositioning
        # See handling for 'Td' operator for how/why this is used.
        cur_displacement: float = 0.0

        def mult(tm: List[float], cm: List[float]) -> List[float]:
            """ Does matrix multiplication with the shortened forms of matrices tm, cm.
                If we don't want to use numpy, can instead copy the mult function from
                pypdf._page.PageObject._extract_text
                See 9.4.2 Tm operator for description of shortened matrix
                """
            mat1 = [[tm[0], tm[1], 0],
                    [tm[2], tm[3], 0],
                    [tm[4], tm[5], 1]]
            mat2 = [[cm[0], cm[1], 0],
                    [cm[2], cm[3], 0],
                    [cm[4], cm[5], 1]]
            result = matmul(mat1, mat2)
            return [result[0,0], result[0,1], result[1,0], result[1,1], result[2,0], result[2,1], result[2,2]]

        def get_content_and_displacement(bs: bytes) -> Tuple[str, float]:
            """Decode byte-string to unicode str and calculate horizontal displacement."""
            content = ''
            displacement = 0.0
            for byte in bs:
                char = chr(byte)
                content += self.font_map_dicts[text_state.f_name][char]
                displacement += self.font_width_dicts[text_state.f_name][char] / 1000 * text_state.size
            return content, displacement

        def terminate_segment() -> None:
            """End the current text segment, adding it to extracted_segments."""
            nonlocal text_state, cur_displacement
            if segment.content != '':
                segment.font_name = self.font_output_names[text_state.f_name]
                # segment = TextSegment(segment.content, x, y, font_output_name)
                extracted_segments.append(copy(segment))
            segment.reset()
            cur_displacement = 0.0

        def operand_visitor(operator, args, cm, tm) -> None:
            """ Visitor function which keeps track of current font being used, and translates pdf text instructions
            to unicode text without inserting any extraneous whitespace.
            """
            nonlocal text_state, cur_displacement

            if operator in (b'TJ', b'Tj') and segment.coordinates is None:
                # We want the output coordinates to be where the segment started, not get updated by 'Td' operations
                m = mult(tm, cm)
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
                # font, font size are included in graphics state.
                text_state_stack.append(text_state)
            elif operator == b'Q':
                # pop from graphics state stack
                terminate_segment()
                text_state = text_state_stack.pop()
            elif operator == b'ET':
                # End text block operator
                terminate_segment()
            elif operator == b'Td':
                # Move text position
                x_transform, y_transform = args
                if abs(y_transform) >= 1:
                    # The 1 here is arbitrary. Every case I've seen with +-<1 unit change is on the same logical line,
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
                    if units_of_spacing > space_threshold * text_state.size:
                        segment.content += self.reader.tab
                        # logger.debug(segment.content + f'{{{units_of_spacing:.1f}>{text_state.size}*{space_threshold:.1f}}}')
                cur_displacement = 0

            elif operator == b'TJ':
                # args will have exactly one element: a list of assorted byte-strings and ints for individual spacing
                for item in args[0]:
                    if isinstance(item, bytes):
                        # add_bytes_to_segment(item)
                        content, displacement = get_content_and_displacement(item)
                        cur_displacement += displacement
                        segment.content += content
                    else:
                        cur_displacement -= item * text_state.size / 1000
            elif operator == b'Tj':
                # args will have exactly one element, a byte-string
                content, displacement = get_content_and_displacement(args[0])
                cur_displacement += displacement
                segment.content += content
            elif operator in (b"'", b'"',):
                # These are text showing operators that aren't used in dockets. If we find docket that does use them,
                # will have to implement to catch all text.
                logger.warning(f"Found unexpected text showing operator: {operator}")
            elif operator in (b'Tc', b'Tw', b'Tz', b'TL', b'Ts', b'T'):
                # These are text state operators that aren't used in dockets. If we find docket that does use them,
                # will have to implement to calculate correct displacement. See 9.3.1
                logger.warning(f"Found unexpected text spacing operator: {operator}")



        def visitor(operator, args, cm, tm) -> None:
            """Visitor function that calls our visitor and also a visitor_operand_before if we were passed one."""
            operand_visitor(operator, args, cm, tm)
            if kwargs.get('visitor_operand_before') is not None:
                kwargs['visitor_operand_before'](operator, args, cm, tm)

        # avoid infinite recursion
        super_kwargs = copy(kwargs)
        super_kwargs['visitor_operand_before'] = visitor
        super().extract_text(**super_kwargs)

        formatted_segments = [self.segment_to_str(seg) for seg in extracted_segments]
        return ''.join(formatted_segments)

    def segment_to_str(self, segment: TextSegment) -> str:
        """Take a TextSegment and return the content of segment plus formatted expression of its properties.
        Terminates with newline character from reader."""
        rounded_coordinates = (round(coordinate,2) for coordinate in segment.coordinates)
        # The grammar currently expects this exact format, so it will need to change if this does.
        properties = ''.join(f'{n:06.2f},' for n in rounded_coordinates)
        properties += segment.font_name
        properties = self.reader.properties_open + properties + self.reader.properties_close
        segment_as_string = segment.content + properties + self.reader.newline
        return segment_as_string



if __name__ == "__main__":
    test_paths = Path(r"platform/docket_parser/tests/data").glob('*.pdf')
    logger.setLevel('INFO')
    for test_path in test_paths:
        _reader = DocketReader(test_path)
        _extracted_text = _reader.extract_text().replace(_reader.newline, '\n')
        out_file_path = Path('scratch/data').joinpath(test_path.name.replace('.pdf', '.txt'))
        with open(out_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(_extracted_text)
        out_file_path = Path('scratch/data').joinpath(test_path.name.replace('.pdf', '.operations'))
        with open(out_file_path, 'w') as out_file:
            for operator, operand in _reader._debug_get_all_operations():
                print(f"{operator} : {operand}", file=out_file)
