"""shift color filter"""

from configparser import ConfigParser

from larry import ColorList, utils


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Shift colors by a random amount"""
    num_colors = len(orig_colors)
    places = utils.randsign(num_colors - 1) or (num_colors - 1)

    if places == 0:
        return orig_colors

    colors = orig_colors[-1 * places :] + orig_colors[: -1 * places]
    return colors
