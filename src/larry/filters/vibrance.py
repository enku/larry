"""vibrance color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorList
from larry.utils import clamp


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Make colors more vibrant

    Given a threshold value, and for colors below this threshold, increase saturation by
    a percentage of the difference between the threshold and the original saturation.
    """
    colors: ColorList = []
    threshold = config.getfloat("filters:vibrance", "threshold", fallback=None)

    if threshold is None:
        threshold = sum(color.to_hsv()[1] for color in orig_colors) / len(orig_colors)

    percentage = config.getint("filters:vibrance", "percent", fallback=20) * 0.01

    for color in orig_colors:
        h, s, v = color.to_hsv()

        if s >= threshold:
            colors.append(color)
            continue

        new_s = clamp(s + percentage * (threshold - s), maximum=100)
        colors.append(Color.from_hsv((h, new_s, v)))

    return colors
