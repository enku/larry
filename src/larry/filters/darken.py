"""darken color filter"""

from configparser import ConfigParser

from larry import Color, ColorList
from larry.color import combine_colors as combine

from .utils import get_opacity, new_image_colors


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Darkens colors with the darkest of two colors"""
    opacity = get_opacity(config, "darken")
    pairs = zip(orig_colors, new_image_colors(len(orig_colors), config, "darken"))

    return [combine(min(fg, bg, key=Color.luminocity), fg, opacity) for fg, bg in pairs]
