"""lighten color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator
from larry.color import combine_colors as combine

from .utils import get_opacity, new_image_colors


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Lighten colors with the lightest of two colors"""
    aux_colors = new_image_colors(num_colors, config, "lighten")
    opacity = get_opacity(config, "lighten")

    for orig_color, aux_color in zip(orig_colors, aux_colors):
        yield combine(
            max(orig_color, aux_color, key=Color.luminocity), orig_color, opacity
        )
