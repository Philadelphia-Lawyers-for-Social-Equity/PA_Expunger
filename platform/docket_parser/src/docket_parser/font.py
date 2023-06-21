import logging

from pypdf._cmap import parse_to_unicode
from pypdf.errors import PdfReadError
from pypdf.generic import DictionaryObject

logger = logging.getLogger(__name__)


class PdfFontWrapper(DictionaryObject):
    """Wrapper for pypdf font, providing useful functions."""

    def __init__(self, font: DictionaryObject) -> None:
        super().__init__(font)
        if font_type := font['/Subtype'] != '/TrueType':
            logger.warning(f"Text extraction is only tested on PDFs with TrueType fonts, not {font_type[1:]}")
        self.unicode_map = self.get_unicode_map()
        self.widths = self.get_widths_dict()

    def get_unicode_map(self) -> dict[int, str]:
        """Return a dictionary mapping character ID (cid's) as ints to unicode characters."""
        if "/ToUnicode" not in self:
            raise PdfReadError(f"Font has no ToUnicode entry:\n{self}")
        unicode_str_map, space_code, int_entry = parse_to_unicode(self, 0)
        # pypdf uses the key -1 in unicode_str_map for internal reasons. We don't need it.
        unicode_str_map.pop(-1)
        # Convert single character str keys to integer keys (0-255)
        unicode_int_map = {ord(cid): unicode_char
                           for cid, unicode_char in unicode_str_map.items()}
        return unicode_int_map

    def get_widths_dict(self) -> dict[int, int]:
        """Return a dictionary mapping int character IDs to their widths."""
        # We could filter out the cids not actually used in font, but that hasn't been necessary
        widths_dict = {}
        for i in range(self['/FirstChar'], self['/LastChar'] + 1):
            widths_dict[i] = self['/Widths'][i - self['/FirstChar']]
        return widths_dict

    def get_content_and_width(self, bs: bytes) -> tuple[str, int]:
        """Decode byte-string to unicode str and calculate horizontal width (in glyph space units)"""
        content = ''
        width = 0
        for character_id in bs:
            content += self.unicode_map[character_id]
            width += self.widths[character_id]
        return content, width
