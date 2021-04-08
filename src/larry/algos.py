"""Color selection algorithms"""
import random
from configparser import ConfigParser
from typing import Callable

import pkg_resources

from larry import LOGGER, Color, ColorList, Image, randsign
from larry.io import read_file


class AlgoNotFound(LookupError):
    """Unable to find the requested plugin"""


def load_algo(name: str) -> Callable:
    """Load the algo with the given name"""
    iter_ = pkg_resources.iter_entry_points("larry.algos", name)

    try:
        return next(iter_).load()
    except (ModuleNotFoundError, StopIteration) as error:
        raise AlgoNotFound(name) from error


def algos_list():
    return [(i.name, i.load()) for i in pkg_resources.iter_entry_points("larry.algos")]


def luminocity_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return colors with the same luminocity as the original"""
    return [Color.randcolor(lum=i.luminocity()) for i in orig_colors]


def inverse_algo(orig_colors: ColorList, _config: ConfigParser):
    """Return `luminocity_algo of orig_colors inversed"""
    return [i.inverse() for i in orig_colors]


def gradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return gradient within the same luminocity range as the orignal"""
    fuzz = config.getint("algos:gradient", "fuzz", fallback=0)

    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 0])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 255])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )

    return [*colors]


def zipgradient_algo(orig_colors: ColorList, config: ConfigParser):
    """Return the result of n gradients zipped"""
    num_colors = len(orig_colors)
    gradient_count = config.getint("algos:zipgradient", "colors", fallback=2)
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


def shuffle(orig_colors: ColorList, _config: ConfigParser):
    """Shuffle the rgb for each color

    But keep the same saturation and brightness as the original
    """
    colors = []

    for orig_color in orig_colors:
        rgb = [*orig_color]
        random.shuffle(rgb)
        tmp_color = Color(*rgb)
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
    try:
        include_str = config["algos:random"]["include"]
    except KeyError:
        algo_names = [*{i.name for i in pkg_resources.iter_entry_points("larry.algos")}]
        algo_names.remove("random")
    else:
        algo_names = [*{i.strip() for i in include_str.split()}]

    if not algo_names:
        return orig_colors

    try:
        chains = int(config["algos:random"]["chains"])
    except (KeyError, ValueError):
        chains = 1

    new_colors = orig_colors
    iters = random.randint(1, chains)

    for _ in range(iters):
        algo_name = random.choice(algo_names)
        algo = load_algo(algo_name)
        LOGGER.debug("random: running algo: %s", algo_name)
        new_colors = algo(new_colors, config)

    return new_colors


def brighten(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return brightened (or darkend) version of the colors"""
    percent = config.getint("algos:brighten", "percent", fallback=-20)
    colors: ColorList = []

    for color in orig_colors:
        lum = color.luminocity()
        new_lum = lum + 0.01 * percent * lum
        colors.append(color.luminize(new_lum))

    return colors


def subtract(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """XXX"""
    color = random.choice(orig_colors)
    sign = random.choice([-1, 1])

    if sign == -1:
        return [i - color for i in orig_colors]

    return [i + color for i in orig_colors]


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
    source = config.get("algos:swap", "source", fallback=None)
    if source is None:
        source_colors = [
            Color(0, 0, 0),
            Color(28, 52, 63),
            Color(37, 67, 81),
            Color(102, 102, 102),
            Color(124, 142, 150),
            Color(255, 255, 255),
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


def vga(orig_colors: ColorList, config: ConfigParser):
    """A blast from the past"""
    colors: ColorList = []
    bits = config.getint("algos:vga", "bits", fallback=8)
    div = 256 / bits

    for color in orig_colors:
        red, green, blue = color
        red = red // div * div
        green = green // div * div
        blue = blue // div * div
        colors.append(Color(red, green, blue))

    return colors


def grayscale(orig_colors: ColorList, config: ConfigParser):
    """Convert colors to grayscale"""
    num_grays = config.getint("algos:grayscale", "grays", fallback=512)
    div = 255 / num_grays
    black = Color(0, 0, 0)
    white = Color(255, 255, 255)
    grays = [*Color.gradient(black, white, num_grays)]
    colors: ColorList = []

    for color in orig_colors:
        lum = color.luminocity()
        colors.append(grays[int(lum // div) - 1])

    return colors


def reduce(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Reduce the number of distinct colors"""
    if not orig_colors:
        return []

    percent: int = 10

    try:
        percent: int = config["algos:reduce"].getint("amount", fallback=percent)
    except KeyError:
        pass

    if percent == 0:
        return orig_colors

    amount = int(percent / 100 * len(orig_colors))

    last_color = orig_colors[0]
    new_colors = [last_color]

    for i, color in enumerate(orig_colors[1:], start=1):
        if i % amount == 0:
            last_color = color

        new_colors.append(last_color)

    return new_colors
