"""randbright color filter"""

import random
from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """Each color is darkened/lightened by a random value"""
    for color in orig_colors:
        yield color.luminize(random.randint(0, 255))
