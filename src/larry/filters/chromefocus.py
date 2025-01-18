"""chromefocus color filter"""

import collections
from configparser import ConfigParser

from larry import utils
from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, _num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Focus on a particular color and fade out the others"""
    focus_range = config.getfloat("filters:chromefocus", "range", fallback=5.0)

    if focus_range == 0:
        yield from orig_colors
        return

    factor = config.getfloat("filters:chromefocus", "factor", fallback=0.0)
    buckets = utils.buckets(0, 360, focus_range)
    hue_counts: collections.Counter[tuple[float, float]] = collections.Counter()

    colors = list(orig_colors)
    for color in colors:
        hue = color.to_hsv()[0]
        for bucket in buckets:
            if bucket[0] <= hue < bucket[1]:
                hue_counts.update([bucket])
                break

    average_hue = sum(hue_counts.most_common(1)[0][0]) / 2

    for color in colors:
        h, s, v = color.to_hsv()
        if utils.angular_distance(h, average_hue) <= focus_range:
            yield color
        else:
            yield Color.from_hsv((h, factor * s, v))
