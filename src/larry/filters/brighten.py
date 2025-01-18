"""brighten color filter"""

from configparser import ConfigParser

from larry.color import ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Return brightened (or darkend) version of the colors"""
    percent = config.getint("filters:brighten", "percent", fallback=-20)

    for color in orig_colors:
        lum = color.luminocity()
        new_lum = lum + 0.01 * percent * lum
        yield color.luminize(new_lum)
