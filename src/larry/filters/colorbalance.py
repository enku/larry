"""colorbalance color filter"""

from configparser import ConfigParser

import numpy as np

from larry.color import Color, ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Adjust the colors to achieve a more harmonious color scheme"""
    normalized = np.array(orig_colors) / 255
    average = normalized.mean(axis=0)
    adjusted = np.clip(normalized + (average - normalized) * 0.5, 0, 1) * 255

    return [Color.from_array(carray) for carray in adjusted]
