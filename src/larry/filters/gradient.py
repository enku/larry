"""gradient color filter"""

from configparser import ConfigParser

from larry import utils
from larry.color import Color, ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Return gradient within the same luminocity range as the original"""
    fuzz = config.getint("filters:gradient", "fuzz", fallback=0)
    colors = list(orig_colors)

    lum1 = max([colors[0].luminocity() + utils.randsign(fuzz), 0])
    lum2 = min([colors[-1].luminocity() + utils.randsign(fuzz), 255])

    return Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(colors)
    )
