"""swap color filter"""

from configparser import ConfigParser

from larry import make_image_from_bytes
from larry.color import Color, ColorGenerator
from larry.io import read_file


def cfilter(
    _orig_colors: ColorGenerator, num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Swap colors from source"""
    source = config.get("filters:swap", "source", fallback=None)
    if source is None:
        source_colors = [
            Color(0, 0, 0),
            Color(28, 52, 63),
            Color(37, 67, 81),
            Color(102, 102, 102),
            Color(124, 142, 150),
            Color(255, 255, 255),
        ]

    else:
        raw_image_data = read_file(source)
        image = make_image_from_bytes(raw_image_data)

        source_colors = list(image.get_colors())

    source_colors.sort(key=Color.luminocity)

    return Color.generate_from(source_colors, num_colors, randomize=False)
