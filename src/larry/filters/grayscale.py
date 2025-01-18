"""grayscale color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Convert colors to grayscale"""
    colors: ColorList = []
    new_saturation = config.getfloat("filters:grayscale", "saturation", fallback=0.0)

    for color in orig_colors:
        hue, _, value = color.to_hsv()
        colors.append(Color.from_hsv((hue, new_saturation, value)))

    return colors
