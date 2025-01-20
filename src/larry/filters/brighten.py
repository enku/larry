"""brighten color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return brightened (or darkend) version of the colors"""
    percent = config.getint("filters:brighten", "percent", fallback=-20)
    colors: ColorList = []

    for color in orig_colors:
        lum = color.luminocity()
        new_lum = lum + 0.01 * percent * lum
        colors.append(color.luminize(new_lum))

    return colors
