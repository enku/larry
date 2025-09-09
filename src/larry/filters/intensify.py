"""Filter to intensify the given colors"""

from configparser import ConfigParser

from larry.color import ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Intensifies the colors (increases saturation)"""
    amount = config.getfloat("filters:intensify", "percent", fallback=50.0) / 100

    return [color.intensify(amount) for color in orig_colors]
