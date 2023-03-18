from pypdf._cmap import parse_to_unicode
from pypdf.generic import DictionaryObject


def get_unicode_map(font: DictionaryObject):
    """Given a font object with a ToUnicode entry, return a dictionary mapping character IDs (cid's)
       to unicode characters."""
    unicode_map, space_code, int_entry = parse_to_unicode(font, 0)
    return unicode_map


def get_widths_dict(font: DictionaryObject):
    """Given a font object, return a dictionary mapping character IDs to their widths."""
    widths_dict = {}
    for i in range(font['/FirstChar'], font['/LastChar'] + 1):
        widths_dict[chr(i)] = font['/Widths'][i - font['/FirstChar']]
    return widths_dict
