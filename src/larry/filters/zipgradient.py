"""zipgradient color filter"""

from configparser import ConfigParser

from larry import Color, ColorList


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return the result of n gradients zipped"""
    num_colors = len(orig_colors)
    gradient_count = config.getint("filters:zipgradient", "colors", fallback=2)
    steps = num_colors // gradient_count

    # You need at least 2 steps to make a gradient
    if steps < 2:
        return orig_colors

    i = steps
    color = Color.randcolor(lum=orig_colors[0].luminocity())

    colors: ColorList = []
    while len(colors) < num_colors:
        next_color = Color.randcolor(
            lum=orig_colors[min(i, num_colors - 1)].luminocity()
        )
        grad = Color.gradient(color, next_color, steps)
        colors += [*grad][1:]
        i += steps
        color = next_color

    return colors[:num_colors]
