"""shift color filter"""

from configparser import ConfigParser

from larry import utils
from larry.color import ColorGenerator


def cfilter(orig_colors: ColorGenerator, _config: ConfigParser) -> ColorGenerator:
    """Shift colors by a random amount"""
    colors = list(orig_colors)
    num_colors = len(colors)
    places = utils.randsign(num_colors - 1) or (num_colors - 1)

    if places == 0:
        yield from colors
        return

    colors = colors[-1 * places :] + colors[: -1 * places]
    yield from colors
