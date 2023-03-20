from copy import copy

from pypdf._cmap import parse_to_unicode
from pypdf.generic import DictionaryObject


def get_unicode_map(font: DictionaryObject):
    """Given a font object with a ToUnicode entry, return a dictionary mapping character ID (cid's) as ints
       to unicode characters."""
    unicode_map, space_code, int_entry = parse_to_unicode(font, 0)
    # pypdf uses the key -1 in unicode_map for internal reasons when parsing the cmap. We don't need it.
    unicode_map.pop(-1)

    # Convert single character str keys to integers (0-255)
    for key, value in copy(unicode_map).items():
        unicode_map[ord(key)] = value
        del unicode_map[key]
    return unicode_map


def get_widths_dict(font: DictionaryObject):
    """Given a font object, return a dictionary mapping character IDs to their widths."""
    widths_dict = {}
    for i in range(font['/FirstChar'], font['/LastChar'] + 1):
        widths_dict[i] = font['/Widths'][i - font['/FirstChar']]
    return widths_dict
