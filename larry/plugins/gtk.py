"""Larry plugin for gtk"""
import os
from typing import List

from larry import Color, rgb, rgba, rrggbb, write_file, ConfigType


def plugin(colors: List[Color], config: ConfigType):
    """gtk.css plugin"""
    theme_color = colors[0]
    template = os.path.expanduser(config["template"])
    outfile = os.path.expanduser(config["location"])
    config_colors = config.get("colors", "").split()

    with open(template) as css_file:
        orig_css = css_file.read()

    new_css = orig_css

    for color in config_colors:
        num_commas = color.count(",")

        if num_commas == 0:
            # rrggbb
            new_css = rrggbb(color, theme_color, new_css)
        elif num_commas == 2:
            # r,g,b
            new_css = rgb(color, theme_color, new_css)
        elif num_commas == 3:
            # r,g,b,a
            new_css = rgba(color, theme_color, new_css)

    write_file(outfile, new_css)
