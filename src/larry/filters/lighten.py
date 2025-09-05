"""lighten color filter"""

from configparser import ConfigParser

from larry import Color, ColorList
from larry.color import combine_colors as combine

from .utils import get_opacity, new_image_colors


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Lighten colors with the lightest of two colors"""
    aux_colors = new_image_colors(orig_colors, config, "lighten")
    opacity = get_opacity(config, "lighten")

    return [
        combine(max(orig_color, aux_color, key=Color.luminocity), orig_color, opacity)
        for orig_color, aux_color in zip(orig_colors, aux_colors)
    ]
