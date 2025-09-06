"""kaleidoscope color filter"""

from configparser import ConfigParser

from larry.color import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Every other color plus the same list reversed"""
    size = len(orig_colors)
    new: ColorList = []
    i = iter(zip(orig_colors, reversed(orig_colors)))
    new = []

    while current := next(i, None):
        new.extend(current)
        next(i, None)
        next(i, None)
        next(i, None)

    return [*new[: -1 if size % 2 else None], *reversed(new)]
