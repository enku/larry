"""soften color filter"""

from configparser import ConfigParser

from larry import ColorList
from larry.color import DEFAULT_SOFTNESS


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Soften all the original colors"""
    softness = config.getfloat("filters:soften", "softness", fallback=DEFAULT_SOFTNESS)

    return [orig_color.soften(softness) for orig_color in orig_colors]
