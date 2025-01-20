"""subtract color filter"""

import random
from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """XXX"""
    color = random.choice(orig_colors)
    sign = random.choice([-1, 1])

    if sign == -1:
        return [i - color for i in orig_colors]

    return [i + color for i in orig_colors]
