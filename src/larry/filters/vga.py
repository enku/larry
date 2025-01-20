"""vga color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """A blast from the past"""
    colors: ColorList = []
    bits = config.getint("filters:vga", "bits", fallback=8)
    div = 256 / bits

    for color in orig_colors:
        red, green, blue = color
        red = int(red // div * div)
        green = int(green // div * div)
        blue = int(blue // div * div)
        colors.append(Color(red, green, blue))

    return colors
