"""swap color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorList
from larry.image import make_image_from_bytes
from larry.io import read_file


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
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

        source_colors = [*image.get_colors()]

    source_colors.sort(key=Color.luminocity)

    return list(Color.generate_from(source_colors, len(orig_colors), randomize=False))
