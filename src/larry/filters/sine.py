"""Change the hue by a ratio of its sine, cosine, or either"""

import math
import random
import sys
from configparser import ConfigParser

from larry.color import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Change the hue by a ratio of its sine"""
    mode = config.get("filters:sine", "mode", fallback="sine")

    match mode:
        case "cosine":
            ratio = cosine_ratio
        case "random":
            ratio = random_ratio
        case "sine":
            ratio = sine_ratio
        case _:
            print(f"Warning: invalid mode: {mode}", file=sys.stderr)
            ratio = sine_ratio

    return [ratio(color) * color for color in orig_colors]


def sine_ratio(color: Color) -> float:
    """Return the color ratio based on the sine of its hue"""
    return 1 + math.sin(math.radians(color.to_hsv()[0]))


def cosine_ratio(color: Color) -> float:
    """Return the color ratio based on the cosine of its hue"""
    return 1 + math.cos(math.radians(color.to_hsv()[0]))


def random_ratio(color: Color) -> float:
    """Randomly choose either sine or cosine ratios and apply to the given color"""
    return random.choice([sine_ratio, cosine_ratio])(color)
