"""hueshift color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Shift the hues of each color by a given amount"""
    amount = config.getfloat("filters:hueshift", "amount", fallback=-90.0)

    return [
        Color.from_hsv((((h + amount) % 360), s, v))
        for color in orig_colors
        for h, s, v in [color.to_hsv()]
    ]
