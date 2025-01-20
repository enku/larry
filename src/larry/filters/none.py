"""none color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """A NO-OP filter

    This is an filter that simply returns the original colors.
    """
    return orig_colors
