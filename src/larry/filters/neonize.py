"""neonize color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return the colors neonized"""
    saturation = config.getfloat("filters:neonize", "saturation", fallback=100.0)
    brightness = config.getfloat("filters:neonize", "brightness", fallback=100.0)

    return [
        Color.from_hsv((h, saturation, brightness))
        for c in orig_colors
        for h in [c.to_hsv()[0]]
    ]
