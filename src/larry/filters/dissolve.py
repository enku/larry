"""dissolve color filter"""

import random
from configparser import ConfigParser

from larry.color import ColorGenerator
from larry.color import combine_colors as combine

from . import FilterError
from .utils import get_opacity, new_image_colors


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Dissolve image into colors from another image"""
    colors = list(orig_colors)
    aux_colors = new_image_colors(len(colors), config, "dissolve")
    opacity = get_opacity(config, "dissolve")

    amount = config["filters:dissolve"].getint("amount", fallback=50)
    if not 0 <= amount <= 100:
        raise FilterError(f"'amount' must be in range [0..100]. Actual {amount}")

    weights = [100 - amount, amount]

    return (
        combine(
            random.choices([orig_color, aux_color], weights, k=1)[0],
            orig_color,
            opacity,
        )
        for orig_color, aux_color in zip(orig_colors, aux_colors)
    )
