"""Larry plugin for gtk"""
from larry import Color, ColorList, ConfigType
from larry.color import rgb, rgba, rrggbb
from larry.io import read_file, write_file


def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    theme_color = next(Color.generate_from(colors, 1))
    template = config["template"]
    outfile = config["location"]
    config_colors = config.get("colors", "").split()

    orig_css = read_file(template).decode()
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

    write_file(outfile, new_css.encode())
