"""zipgradient color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorGenerator


def cfilter(
    orig_colors: ColorGenerator, num_colors: int, config: ConfigParser
) -> ColorGenerator:
    """Return the result of n gradients zipped"""
    colors = list(orig_colors)
    gradient_count = config.getint("filters:zipgradient", "colors", fallback=2)
    steps = num_colors // gradient_count

    # You need at least 2 steps to make a gradient
    if steps < 2:
        yield from colors
        return

    i = steps
    color = Color.randcolor(lum=colors[0].luminocity())

    num_needed = num_colors
    while num_needed > 0:
        next_color = Color.randcolor(lum=colors[min(i, num_colors - 1)].luminocity())
        grad = Color.gradient(color, next_color, steps)
        new_colors = [*grad][1:][:num_needed]
        yield from new_colors
        i += steps
        num_needed -= len(new_colors)
        color = next_color
