"""Larry plugin for gtk"""
from larry import Color, ColorList
from larry.color import replace_string2
from larry.config import ConfigType
from larry.io import read_file, write_file


def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    template = config["template"]
    outfile = config["location"]
    config_colors_strs = config.get("colors", "").split()
    config_colors = []

    for string in config_colors_strs:
        if len(string) == 6:
            config_colors.append(Color(f"#{string}"))
        elif string.count(",") >= 2:
            r, g, b = string.split(",")[:3]
            config_colors.append(Color(int(r.strip()), int(g.strip()), int(b.strip())))

    orig_css = read_file(template).decode()
    new_css = orig_css

    colormap = {color: color.colorify(theme_color) for color in config_colors}
    new_css = replace_string2(orig_css, colormap)

    write_file(outfile, new_css.encode())
