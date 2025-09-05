"""colorify color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Apply a color filter over the colors"""
    color_str = config.get("filters:colorify", "color", fallback="#ff0000")
    color = Color(color_str)

    if config.getboolean("filters:colorify", "pastelize", fallback=True):
        color = color.pastelize()

    fix_bw = config.getboolean("filters:colorify", "fix_bw", fallback=False)

    return [orig_color.colorify(color, fix_bw) for orig_color in orig_colors]
