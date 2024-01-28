"""Larry plugin for gtk"""

from larry import Color, ColorList
from larry.color import COLORS_RE, replace_string
from larry.config import ConfigType
from larry.io import read_file, write_file


def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    template = config["template"]
    outfile = config["location"]
    orig_css = read_file(template).decode()
    orig_colors = list(set(Color(s) for s in COLORS_RE.findall(orig_css)))
    theme_colors = list(Color.generate_from(colors, len(orig_colors)))

    colormap = {
        color: theme_color.colorify(color)
        for color, theme_color in zip(orig_colors, theme_colors)
    }
    new_css = replace_string(orig_css, colormap)

    write_file(outfile, new_css.encode())
