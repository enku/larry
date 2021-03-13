"""Color selection algorithms"""
import itertools
import random
from configparser import ConfigParser

import pkg_resources

from larry import randsign
from larry.io import read_file
from larry.types import Color, ColorList, Image


def luminocity_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return colors with the same luminocity as the original"""
    return [Color.randcolor(lum=i.luminocity()) for i in orig_colors]


def inverse_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return `luminocity_algo of orig_colors inversed"""
    return gradient_algo([i.inverse() for i in orig_colors], _config)


def gradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return gradient within the same luminocity range as the orignal"""
    fuzz = config.getint("larry", "fuzz", fallback=0)

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 0])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 255])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )

    return [*colors]


def zipgradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return the result of n gradients zipped"""
    fuzz = config.getint("larry", "fuzz", fallback=0)
    gradient_count = config.getint("larry", "zipgradient_colors", fallback=2)

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 0])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 255])

    gradients = [
        Color.gradient(
            Color.randcolor(lum=lum1),
            Color.randcolor(lum=lum2),
            len(orig_colors) // gradient_count,
        )
        for i in range(gradient_count)
    ]
    colors = itertools.chain(*zip(*gradients))

    return [*colors]


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


def brighten(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    percent = config.getint("algos:brighten", "percent", fallback=-20)
    colors: ColorList = []

    for color in orig_colors:
        lum = color.luminocity()
        new_lum = lum + 0.01 * percent * lum
        colors.append(color.luminize(new_lum))

    return colors


def subtract(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    # pick a random color
    color = random.choice(orig_colors)

    # subtract it from all the colors
    return [i - color for i in orig_colors]


def randbright(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Each color is darkened/lightened by a random value"""
    return [i.luminize(random.randint(0, 255)) for i in orig_colors]


def contrast(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """The darks are so dark and the brights are so bright"""
    num_colors = len(orig_colors)
    step = 255 / num_colors

    colors = []
    lum = 0.0
    for color in orig_colors:
        colors.append(color.luminize(lum))
        lum += step

    return colors


def swap(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Swap colors from source"""
    if source := config.get("algos:swap", "source"):
        source_colors = [
            Color((0, 0, 0)),
            Color((28, 52, 63)),
            Color((37, 67, 81)),
            Color((102, 102, 102)),
            Color((124, 142, 150)),
            Color((255, 255, 255)),
        ]

    else:
        raw_image_data = read_file(source)
        image = Image.from_bytes(raw_image_data)

        source_colors = [*image.get_colors()]

    source_colors.sort(key=Color.luminocity)

    return [*Color.generate_from(source_colors, len(orig_colors), randomize=False)]


def noop(orig_colors: ColorList, _config: ConfigParser):
    """A NO-OP algo

    This is an algo that simply returns the original colors.
    """
    return list(orig_colors)
