import logging

from pypdf._cmap import _parse_to_unicode
from pypdf.errors import PdfReadError
from pypdf.generic import DictionaryObject

logger = logging.getLogger(__name__)


class PdfFontWrapper(DictionaryObject):
    """Wrapper for pypdf font, providing useful functions."""

    def __init__(self, font: DictionaryObject) -> None:
        super().__init__(font)
        if font_type := font['/Subtype'] != '/TrueType':
            logger.warning(f"Text extraction is only tested on PDFs with TrueType fonts, not {font_type[1:]}")
        self.cid_to_unicode_map = self.get_unicode_maps()
        self.unicode_to_cid_map = {value: key for key, value in self.cid_to_unicode_map.items()}
        self.cid_widths, self.unicode_widths = self.get_widths_dicts()

    def get_unicode_maps(self) -> dict[int, str]:
        """Return a dictionary mapping character ID (cid's) as ints to unicode characters."""
        if "/ToUnicode" not in self:
            raise PdfReadError(f"Font has no ToUnicode entry:\n{self}")
        unicode_str_map, int_entry = _parse_to_unicode(self)
        # pypdf uses the key -1 in unicode_str_map for internal reasons. We don't need it.
        unicode_str_map.pop(-1)
        # Convert single character str keys to integer keys (0-255)
        unicode_int_map = {ord(cid): unicode_char
                           for cid, unicode_char in unicode_str_map.items()}
        return unicode_int_map

    def get_widths_dicts(self) -> tuple[dict[int, int], dict[str, int]]:
        """Return two dictionaries. The first maps int character IDs to their widths,
        and the second maps unicode characters to their widths."""
        cid_widths_dict = {}
        unicode_widths_dict = {}
        for i in range(self['/FirstChar'], self['/LastChar'] + 1):
            if i not in self.cid_to_unicode_map:
                continue

            cid_width = self['/Widths'][i - self['/FirstChar']]

            cid_widths_dict[i] = cid_width

            unicode_char = self.cid_to_unicode_map[i]
            unicode_widths_dict[unicode_char] = cid_width
        return cid_widths_dict, unicode_widths_dict

    def get_content_and_width(self, bs: bytes) -> tuple[str, int]:
        """Decode byte-string to unicode str and calculate horizontal width (in glyph space units)"""
        content = ''
        width = 0
        for character_id in bs:
            content += self.cid_to_unicode_map[character_id]
            width += self.cid_widths[character_id]
        return content, width

    def get_unicode_string_width(self, string: str) -> int:
        """Calculate the width that a unicode string has with this font, in glyph space units"""
        return sum(self.unicode_widths[char] for char in string)

    def get_unicode_characters(self):
        return list(self.unicode_to_cid_map.keys())

    def unicode_to_bytestring(self, string: str) -> bytes:
        return bytes((self.unicode_to_cid_map[char] for char in string))
