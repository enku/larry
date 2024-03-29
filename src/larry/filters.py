"""Color selection filters"""

import collections
import io
import math
import random as rand
import typing as t
from configparser import ConfigParser
from importlib.metadata import entry_points
from itertools import cycle

from larry import LOGGER, Color, ColorList, make_image_from_bytes, utils
from larry.color import DEFAULT_SOFTNESS
from larry.color import combine_colors as combine
from larry.config import load as load_config
from larry.io import read_file

Filter = t.Callable[[ColorList, ConfigParser], ColorList]


class FilterNotFound(LookupError):
    """Unable to find the requested filter"""


class FilterError(RuntimeError):
    """Filter cannot run successfully"""


def list_filters(config_path: str) -> str:
    """Return text displaying available filters and enabled status"""
    output = io.StringIO()
    config = load_config(config_path)
    enabled_filter = config["larry"].get("filter", "gradient").split()

    for name, func in filters_list():
        func_doc = func.__doc__ or ""
        doc = func_doc.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_filter else " "

        print(f"[{enabled}] {name:20} {doc}", file=output)

    return output.getvalue()


def load_filter(name: str) -> Filter:
    """Load the filter with the given name"""
    filters = entry_points().select(group="larry.filters", name=name)

    if not filters:
        raise FilterNotFound(name)

    try:
        return tuple(filters)[0].load()
    except ModuleNotFoundError as error:
        raise FilterNotFound(name) from error


def filters_list() -> list[tuple[str, Filter]]:
    """Return a list of tuple of (filter_name, filter_func) for all filters"""
    return [(i.name, i.load()) for i in entry_points().select(group="larry.filters")]


def luminocity(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Return colors with the same luminocity as the original"""
    return [Color.randcolor(lum=i.luminocity()) for i in orig_colors]


def inverse(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Return orig_colors inversed"""
    return [i.inverse() for i in orig_colors]


def gradient(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return gradient within the same luminocity range as the original"""
    fuzz = config.getint("filters:gradient", "fuzz", fallback=0)

    lum1 = max([orig_colors[0].luminocity() + utils.randsign(fuzz), 0])
    lum2 = min([orig_colors[-1].luminocity() + utils.randsign(fuzz), 255])

    colors = Color.gradient(
        Color.randcolor(lum=lum1), Color.randcolor(lum=lum2), len(orig_colors)
    )

    return [*colors]


def zipgradient(orig_colors: ColorList, config: ConfigParser) -> ColorList:
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


def shuffle(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Shuffle the rgb for each color

    But keep the same saturation and brightness as the original
    """
    colors = []

    for orig_color in orig_colors:
        rgb = [*orig_color]
        rand.shuffle(rgb)
        tmp_color = Color(*rgb)
        saturation, brightness = orig_color.to_hsv()[1:]
        hue = tmp_color.to_hsv()[0]
        color = Color.from_hsv((hue, saturation, brightness))
        colors.append(color)

    return colors


def shift(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Shift colors by a random amount"""
    colors = list(orig_colors)
    num_colors = len(colors)
    places = utils.randsign(num_colors - 1) or (num_colors - 1)

    if places == 0:
        return colors

    colors = colors[-1 * places :] + colors[: -1 * places]
    return colors


def pastelize(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Pastelize all the original colors"""
    return [orig_color.pastelize() for orig_color in orig_colors]


def soften(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Pastelize all the original colors"""
    softness = config.getfloat("filters:soften", "softness", fallback=DEFAULT_SOFTNESS)

    return [orig_color.soften(softness) for orig_color in orig_colors]


def random(
    orig_colors: ColorList, config: ConfigParser
) -> ColorList:  # pragma: no cover
    """Yeah, coz how could we live without a random filter?"""
    try:
        include_str = config["filters:random"]["include"]
    except KeyError:
        filter_names = [*{i.name for i in entry_points().select(group="larry.filters")}]
        filter_names.remove("random")
    else:
        filter_names = [*{i.strip() for i in include_str.split()}]

    if not filter_names:
        return orig_colors

    chains = config["filters:random"].getint("chains", fallback=1)

    new_colors = orig_colors
    iters = rand.randint(1, chains)

    for _ in range(iters):
        filter_name = rand.choice(filter_names)
        filter_ = load_filter(filter_name)
        LOGGER.debug("random: running filter: %s", filter_name)
        new_colors = filter_(new_colors, config)

    return new_colors


def brighten(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Return brightened (or darkend) version of the colors"""
    percent = config.getint("filters:brighten", "percent", fallback=-20)
    colors: ColorList = []

    for color in orig_colors:
        lum = color.luminocity()
        new_lum = lum + 0.01 * percent * lum
        colors.append(color.luminize(new_lum))

    return colors


def subtract(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """XXX"""
    color = rand.choice(orig_colors)
    sign = rand.choice([-1, 1])

    if sign == -1:
        return [i - color for i in orig_colors]

    return [i + color for i in orig_colors]


def randbright(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Each color is darkened/lightened by a random value"""
    return [i.luminize(rand.randint(0, 255)) for i in orig_colors]


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
    source = config.get("filters:swap", "source", fallback=None)
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
        image = make_image_from_bytes(raw_image_data)

        source_colors = [*image.get_colors()]

    source_colors.sort(key=Color.luminocity)

    return [*Color.generate_from(source_colors, len(orig_colors), randomize=False)]


def none(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """A NO-OP filter

    This is an filter that simply returns the original colors.
    """
    return list(orig_colors)


def vga(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """A blast from the past"""
    colors: ColorList = []
    bits = config.getint("filters:vga", "bits", fallback=8)
    div = 256 / bits

    for color in orig_colors:
        red, green, blue = color
        red = int(red // div * div)
        green = int(green // div * div)
        blue = int(blue // div * div)
        colors.append(Color(red, green, blue))

    return colors


def grayscale(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Convert colors to grayscale"""
    colors: ColorList = []
    new_saturation = config.getfloat("filters:grayscale", "saturation", fallback=0.0)

    for color in orig_colors:
        hue, _, value = color.to_hsv()
        colors.append(Color.from_hsv((hue, new_saturation, value)))

    return colors


def reduce(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Reduce the number of distinct colors"""
    num_colors = len(orig_colors)
    amount = num_colors // 20

    try:
        amount = config["filters:reduce"].getint("amount", fallback=amount)
    except KeyError:
        pass

    if amount == 0:
        return orig_colors

    num_chunks = num_colors // amount
    middle = math.ceil(num_chunks / 2)

    return [orig_colors[i] for i in range(middle, num_colors, num_chunks)]


def subgradient(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Like zipgradient, but gradients are a subset of the original colors"""
    num_colors = len(orig_colors)
    index = 0
    size = num_colors // 20
    new_colors: ColorList = []

    try:
        size = config["filters:subgradient"].getint("size", fallback=size)
    except KeyError:
        pass

    if size < 2:
        return orig_colors

    while chunk := orig_colors[index : index + size]:
        grad = Color.gradient(chunk[0], chunk[-1], size)
        new_colors.extend(grad)
        index += size

    return new_colors


def colorify(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Apply a color filter over the colors"""
    color_str = config["filters:colorify"].get("color", fallback="#ff0000")
    color = Color(color_str)

    if config["filters:colorify"].getboolean("pastelize", fallback=True):
        color = color.pastelize()

    fix_bw = config["filters:colorify"].getboolean("fix_bw", fallback=False)

    return [orig_color.colorify(color, fix_bw) for orig_color in orig_colors]


def dissolve(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Dissolve image into colors from another image"""
    aux_colors = new_image_colors(len(orig_colors), config, "dissolve")
    opacity = get_opacity(config, "dissolve")

    amount = config["filters:dissolve"].getint("amount", fallback=50)
    if not 0 <= amount <= 100:
        raise FilterError(f"'amount' must be in range [0..100]. Actual {amount}")

    weights = [100 - amount, amount]

    return [
        combine(
            rand.choices([orig_color, aux_color], weights, k=1)[0], orig_color, opacity
        )
        for orig_color, aux_color in zip(orig_colors, aux_colors)
    ]


def darken(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Darkens colors with the darkest of two colors"""
    aux_colors = new_image_colors(len(orig_colors), config, "darken")
    opacity = get_opacity(config, "darken")

    return [
        combine(min(orig_color, aux_color, key=Color.luminocity), orig_color, opacity)
        for orig_color, aux_color in zip(orig_colors, aux_colors)
    ]


def lighten(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Lighten colors with the lightest of two colors"""
    aux_colors = new_image_colors(len(orig_colors), config, "lighten")
    opacity = get_opacity(config, "lighten")

    return [
        combine(max(orig_color, aux_color, key=Color.luminocity), orig_color, opacity)
        for orig_color, aux_color in zip(orig_colors, aux_colors)
    ]


def chromefocus(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Focus on a particular color and fade out the others"""
    focus_range = config.getfloat("filters:chromefocus", "range", fallback=5.0)

    if focus_range == 0:
        return list(orig_colors)

    factor = config.getfloat("filters:chromefocus", "factor", fallback=0.0)
    buckets = utils.buckets(0, 360, focus_range)
    hue_counts: collections.Counter[tuple[float, float]] = collections.Counter()

    for color in orig_colors:
        hue = color.to_hsv()[0]
        for bucket in buckets:
            if bucket[0] <= hue < bucket[1]:
                hue_counts.update([bucket])
                break

    average_hue = sum(hue_counts.most_common(1)[0][0]) / 2

    colors = []
    for color in orig_colors:
        h, s, v = color.to_hsv()
        if utils.angular_distance(h, average_hue) <= focus_range:
            colors.append(color)
        else:
            colors.append(Color.from_hsv((h, factor * s, v)))
            continue

    return colors


def get_opacity(config: ConfigParser, section: str, name: str = "opacity") -> float:
    """Return the opacity setting from the config & section

    If the opacity value is not valid, raise FilterError.
    """
    opacity = config[f"filters:{section}"].getfloat(name, fallback=1.0)

    if not 0 <= opacity <= 1:
        raise FilterError(f"'opacity' must be in range [0..1]. Actual {opacity}")

    return opacity


def new_image_colors(
    count: int, config: ConfigParser, section: str, name: str = "image"
) -> ColorList:
    """Return count colors from the image specified in config

    If the image has fewer colors than requested, the colors are cycled.
    """
    image_colors = list(
        make_image_from_bytes(
            read_file(config[f"filters:{section}"].get(name))
        ).get_colors()
    )
    if config[f"filters:{section}"].getboolean("shuffle", fallback=False):
        rand.shuffle(image_colors)
    replacer_colors_cycle = cycle(image_colors)

    return [next(replacer_colors_cycle) for _ in range(count)]
