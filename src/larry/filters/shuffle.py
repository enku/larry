"""shuffle color filter"""

import random
from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Shuffle the rgb for each color

    But keep the same saturation and brightness as the original
    """
    colors = []

    for orig_color in orig_colors:
        rgb = [*orig_color]
        random.shuffle(rgb)
        tmp_color = Color(*rgb)
        saturation, brightness = orig_color.to_hsv()[1:]
        hue = tmp_color.to_hsv()[0]
        color = Color.from_hsv((hue, saturation, brightness))
        colors.append(color)

    return colors
