"""darken color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator
from larry.color import combine_colors as combine

from .utils import get_opacity, new_image_colors


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Darkens colors with the darkest of two colors"""
    colors = list(orig_colors)
    aux_colors = new_image_colors(len(colors), config, "darken")
    opacity = get_opacity(config, "darken")

    return (
        combine(min(orig_color, aux_color, key=Color.luminocity), orig_color, opacity)
        for orig_color, aux_color in zip(colors, aux_colors)
    )
