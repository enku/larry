"""contrast color filter"""

from configparser import ConfigParser

from larry import ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """The darks are so dark and the brights are so bright"""
    num_colors = len(orig_colors)
    step = 255 / num_colors

    colors = []
    lum = 0.0
    for color in orig_colors:
        colors.append(color.luminize(lum))
        lum += step

    return colors
