"""vga color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """A blast from the past"""
    bits = config.getint("filters:vga", "bits", fallback=8)
    div = 256 / bits

    for color in orig_colors:
        red, green, blue = color
        red = int(red // div * div)
        green = int(green // div * div)
        blue = int(blue // div * div)
        yield Color(red, green, blue)
