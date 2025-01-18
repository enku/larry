"""none color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """A NO-OP filter

    This is an filter that simply returns the original colors.
    """
    return orig_colors
