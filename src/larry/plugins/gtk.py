"""Larry plugin for gtk"""

from larry import Color, ColorList
from larry.color import COLORS_RE, replace_string
from larry.config import ConfigType
from larry.io import read_file, write_file

DEFAULT_GRAY_THRESHOLD = 35


def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    template = config["template"]
    outfile = config["location"]
    gray_threshold = config.getint("grey_threshold", fallback=DEFAULT_GRAY_THRESHOLD)
    orig_css = read_file(template).decode()
    orig_colors = set(Color(s) for s in COLORS_RE.findall(orig_css))

    colormap = {
        color: color.colorify(theme_color)
        for color in orig_colors
        if not color.is_gray(threshold=gray_threshold)
    }
    new_css = replace_string(orig_css, colormap)

    write_file(outfile, new_css.encode())
