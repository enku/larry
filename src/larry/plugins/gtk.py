"""Larry plugin for gtk"""

from larry import Color, ColorList
from larry.color import COLORS_RE, replace_string, ungray
from larry.config import ConfigType
from larry.io import read_file, write_text_file

DEFAULT_GRAY_THRESHOLD = 35


async def plugin(colors: ColorList, config: ConfigType):
    """gtk.css plugin"""
    theme_color = next(Color.generate_from(colors, 1, randomize=False))
    template = config["template"]
    outfile = config["location"]
    orig_css_bytes = read_file(template)
    orig_css = orig_css_bytes.decode()
    orig_colors = set(Color(s) for s in COLORS_RE.findall(orig_css))

    colormap = {
        color: ungray([color])[0].colorify(theme_color) for color in orig_colors
    }
    new_css = replace_string(orig_css, colormap)

    write_text_file(outfile, new_css)
