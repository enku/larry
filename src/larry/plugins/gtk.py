"""Larry plugin for gtk"""
from larry import Color, ColorList, ConfigType
from larry.color import replace_string
from larry.io import read_file, write_file


def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    template = config["template"]
    outfile = config["location"]
    config_colors = config.get("colors", "").split()

    orig_css = read_file(template).decode()
    new_css = orig_css

    for color in config_colors:
        new_css = replace_string(new_css, color, theme_color)

    write_file(outfile, new_css.encode())
