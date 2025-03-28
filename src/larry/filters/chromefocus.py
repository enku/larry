"""chromefocus color filter"""

import collections
from configparser import ConfigParser

from larry import Color, ColorList, utils


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Focus on a particular color and fade out the others"""
    angular_distance = utils.angular_distance
    focus_range = config.getfloat("filters:chromefocus", "range", fallback=5.0)

    if focus_range == 0:
        return list(orig_colors)

    factor = config.getfloat("filters:chromefocus", "factor", fallback=0.0)
    buckets = utils.buckets(0, 360, focus_range)
    hue_counts: collections.Counter[tuple[float, float]] = collections.Counter()

    for color in orig_colors:
        hue = color.to_hsv()[0]
        for bucket in buckets:
            if bucket[0] <= hue < bucket[1]:
                hue_counts.update([bucket])
                break

    average_hue = sum(hue_counts.most_common(1)[0][0]) / 2

    return [
        (
            color
            if angular_distance(h, average_hue) <= focus_range
            else Color.from_hsv((h, factor * s, v))
        )
        for color in orig_colors
        for h, s, v in [color.to_hsv()]
    ]
