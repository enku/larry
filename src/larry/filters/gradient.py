"""gradient color filter"""

from configparser import ConfigParser

from larry import Color, ColorList, utils


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return gradient within the same luminocity range as the original"""
    fuzz = config.getint("filters:gradient", "fuzz", fallback=0)

    lum1 = max([orig_colors[0].luminocity() + utils.randsign(fuzz), 0])
    lum2 = min([orig_colors[-1].luminocity() + utils.randsign(fuzz), 255])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )

    return list(colors)
