"""shift color filter"""

from configparser import ConfigParser

from larry import ColorList, utils


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Shift colors by a random amount"""
    colors = list(orig_colors)
    num_colors = len(colors)
    places = utils.randsign(num_colors - 1) or (num_colors - 1)

    if places == 0:
        return colors

    colors = colors[-1 * places :] + colors[: -1 * places]
    return colors
