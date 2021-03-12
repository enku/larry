"""Color selection algorithms"""
import itertools
import random
from configparser import ConfigParser
from typing import List

import pkg_resources

from larry import randsign
from larry.types import Color

ColorList = List[Color]

def luminocity_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return colors with the same luminocity as the original"""
    colors = [Color.randcolor(lum=i) for i in [j.luminocity() for j in orig_colors]]

    return colors


def inverse_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return `luminocity_algo of orig_colors inversed"""
    return gradient_algo([i.inverse() for i in orig_colors], _config)


def gradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return gradient within the same luminocity range as the orignal"""
    fuzz = config.getint("larry", "fuzz")

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 1])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 254])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )
    colors = list(colors)

    return colors


def zipgradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return the result of n gradients zipped"""
    fuzz = config.getint("larry", "fuzz")
    gradient_count = config.getint("larry", "zipgradient_colors", fallback=2)

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 1])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 254])

    gradients = [
        Color.gradient(
            Color.randcolor(lum=lum1),
            Color.randcolor(lum=lum2),
            len(orig_colors) // gradient_count,
        )
        for i in range(gradient_count)
    ]
    colors = list(itertools.chain(*zip(*gradients)))

    return colors


def shuffle(orig_colors: ColorList, _config: ConfigParser):
    """Shuffle the rgb for each color.

    But keep the same saturation and brightness as the original
    """
    colors = []

    for orig_color in orig_colors:
        rgb = [orig_color.red, orig_color.green, orig_color.blue]
        random.shuffle(rgb)
        tmp_color = Color(rgb)
        saturation, brightness = orig_color.to_hsv()[1:]
        hue = tmp_color.to_hsv()[0]
        color = Color.from_hsv((hue, saturation, brightness))
        colors.append(color)

    return colors


def shift(orig_colors: ColorList, _config: ConfigParser):
    """Shift colors by a random amount"""
    colors = list(orig_colors)
    num_colors = len(colors)
    places = randsign(num_colors - 1) or (num_colors - 1)

    if places == 0:
        return colors

    colors = colors[-1 * places :] + colors[: -1 * places]
    return colors


def pastelize(orig_colors: ColorList, _config: ConfigParser):
    """Pastelize all the original colors"""
    return [orig_color.pastelize() for orig_color in orig_colors]


def random_algo(orig_colors: ColorList, config: ConfigParser):
    """Yeah, coz how could we live without a random algo?"""
    exclude = ["random"]

    try:
        exclude_str = config["algos:random"]["exclude"]
    except KeyError:
        pass
    else:
        exclude += [i.strip() for i in exclude_str.split()]

    plugins = [
        i
        for i in pkg_resources.iter_entry_points("larry.algos")
        if i.name not in exclude
    ]
    chains = 1

    try:
        chains = int(config["algos:random"]["chains"])
    except KeyError:
        pass

    new_colors = list(orig_colors)
    iters = random.randint(1, chains)

    for _ in range(iters):
        plugin = random.choice(plugins)
        algo = plugin.load()
        new_colors = algo(new_colors, config)

    return new_colors


def noop(orig_colors: ColorList, _config: ConfigParser):
    """A NO-OP algo

    This is an algo that simply returns the original colors.
    """
    return list(orig_colors)
