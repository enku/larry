"""soften color filter"""

from configparser import ConfigParser

from larry.color import DEFAULT_SOFTNESS, ColorGenerator


def cfilter(orig_colors: ColorGenerator, config: ConfigParser) -> ColorGenerator:
    """Pastelize all the original colors"""
    softness = config.getfloat("filters:soften", "softness", fallback=DEFAULT_SOFTNESS)

    for color in orig_colors:
        yield color.soften(softness)
