"""colorify color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Apply a color filter over the colors"""
    color_str = config["filters:colorify"].get("color", fallback="#ff0000")
    color = Color(color_str)

    if config["filters:colorify"].getboolean("pastelize", fallback=True):
        color = color.pastelize()

    fix_bw = config["filters:colorify"].getboolean("fix_bw", fallback=False)

    return (orig_color.colorify(color, fix_bw) for orig_color in orig_colors)
