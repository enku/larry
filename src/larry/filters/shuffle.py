"""shuffle color filter"""

import random
from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, _config: ConfigParser
) -> ColorGenerator:
    """Shuffle the rgb for each color

    But keep the same saturation and brightness as the original
    """
    for orig_color in orig_colors:
        rgb = [*orig_color]
        random.shuffle(rgb)
        tmp_color = Color(*rgb)
        saturation, brightness = orig_color.to_hsv()[1:]
        hue = tmp_color.to_hsv()[0]
        yield Color.from_hsv((hue, saturation, brightness))
