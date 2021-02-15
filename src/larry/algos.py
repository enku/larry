"""Color selection algorithms"""
import itertools

from larry import randsign
from larry.types import Color


def luminocity_algo(orig_colors, _config):
    """Return colors with the same luminocity as the original"""
    colors = [Color.randcolor(lum=i) for i in [j.luminocity() for j in orig_colors]]

    return colors


def inverse_algo(orig_colors, _config):
    """Return `luminocity_algo of orig_colors inversed"""
    return gradient_algo([i.inverse() for i in orig_colors], _config)


def gradient_algo(orig_colors, config):
    """Return gradient within the same luminocity range as the orignal"""
    fuzz = config.getint("larry", "fuzz")

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 1])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 254])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )
    colors = list(colors)

    return colors


def zipgradient_algo(orig_colors, config):
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
