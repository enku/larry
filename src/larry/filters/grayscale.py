"""grayscale color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Convert colors to grayscale"""
    new_saturation = config.getfloat("filters:grayscale", "saturation", fallback=0.0)

    for color in orig_colors:
        hue, _, value = color.to_hsv()
        yield Color.from_hsv((hue, new_saturation, value))
