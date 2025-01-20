"""randbright color filter"""

import random
from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Each color is darkened/lightened by a random value"""
    return [i.luminize(random.randint(0, 255)) for i in orig_colors]
