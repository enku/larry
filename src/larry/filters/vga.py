"""vga color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """A blast from the past"""
    bits = config.getint("filters:vga", "bits", fallback=8)
    div = 256 / bits

    return [
        Color(int(red // div * div), int(green // div * div), int(blue // div * div))
        for color in orig_colors
        for red, green, blue in [color]
    ]
