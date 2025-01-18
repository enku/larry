"""shift color filter"""

from configparser import ConfigParser
from itertools import islice

from larry import utils
from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """Shift colors by a random amount"""
    places = utils.randsign(num_colors - 1) or (num_colors - 1)

    if places == 0 or num_colors == 1:
        yield from orig_colors
        return

    if places > 0:
        tail = list(islice(orig_colors, num_colors - places))
        head = orig_colors
    else:
        tail = list(islice(orig_colors, -1 * places))
        head = orig_colors

    yield from head
    yield from tail
