"""Replace colors on the Larry the Cow wallpaper"""
import argparse
import asyncio
import configparser
import functools
import logging
import operator
import os
import random
import re
import signal
import subprocess
import sys
from typing import Callable, List, MutableMapping, Optional, Set, Tuple, TypeVar, Union

import aionotify
import pkg_resources

__version__ = "1.6.1"

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
COLOR_RE = re.compile(
    r"""
    (
        \#[0-9a-f]{6}|          # rrggbb
        \#[0-9]a-f{3}|          # rgb
        rgb\(\d+, *\d+, *\d+\)  # rgb(d, d, d)
    )
""",
    flags=re.X | re.I,
)
ORIG_SVG_FILENAME = os.path.join(DATA_DIR, "gentoo-cow-gdm-remake.svg")
INTERVAL = 8 * 60
LOGGER = logging.getLogger("larry")
HANDLER = None
CONFIG_PATH = os.path.expanduser("~/.config/larry.cfg")
CONFIG = configparser.ConfigParser()
CONFIG["DEFAULT"]["input"] = ORIG_SVG_FILENAME
CONFIG["DEFAULT"]["fuzz"] = "10"
CONFIG.read(CONFIG_PATH)
_COMPS = (">", "<", "=")

ColorSpecType = Union[str, "Color", Tuple[int, int, int]]
ConfigType = MutableMapping[str, str]
PluginType = Callable[[List["Color"], ConfigType], None]

PLUGINS = {}  # type: MutableMapping[str, PluginType]


class BadColorSpecError(ValueError):
    pass


# The following class was written a *long* time ago in Python 2.x and
# was in a different package. It was hastily ported here and either
# needs to be cleaned up or replaced with a different package.
class Color(object):
    """tuple-like color class"""

    PASTEL_SATURATION = 50
    PASTEL_BRIGHTNESS = 100
    RGB_FILENAME = "/usr/share/X11/rgb.txt"
    rgb = {}  # type: MutableMapping[str, Tuple[int, int, int]]

    def __init__(self, colorspec: ColorSpecType = "random") -> None:
        self.colorspec = colorspec

        if not self.rgb:
            self.load_rgb()

        self.red = self.green = self.blue = 0

        if isinstance(colorspec, Color):
            # copy color
            self.red, self.green, self.blue = (
                colorspec.red,
                colorspec.green,
                colorspec.blue,
            )
            return

        if isinstance(colorspec, str):
            self._handle_str_colorspec(colorspec)

        ####(r, g , b)
        elif isinstance(colorspec, (tuple, list)):
            self.red, self.green, self.blue = [int(i) for i in colorspec]

        else:
            raise BadColorSpecError(repr(colorspec))

        self.color_string = str(self)

    def _handle_str_colorspec(self, colorspec: str):
        """Handle *colorspec* of type str"""
        self.color_string = colorspec
        colorspec = colorspec.strip('"')
        string_type = True

        ###rbg(r, g, b)
        if colorspec.startswith("rgb("):
            parts = colorspec[4:-2].split(",")
            self.red, self.green, self.blue = [int(i.strip()) for i in parts]
            return

        ####r/g/b
        if len(colorspec.split("/")) == 3:
            parts = colorspec.split("/")
            self.red, self.green, self.blue = [int(i) for i in parts]
            return

        ####{ r, g, b}
        if colorspec[0] == "{" and colorspec[-1] == "}":
            red, green, blue = colorspec[1:-1].split(",")
            self.red = int(float(red) * 255)
            self.green = int(float(green) * 255)
            self.blue = int(float(blue) * 255)
            return

        if colorspec.lower() in self.rgb:
            self.red, self.green, self.blue = self.rgb[colorspec.lower()]
            return

        ####random
        if colorspec == "random":
            somecolor = self.randcolor()
            self.red = somecolor.red
            self.blue = somecolor.blue
            self.green = somecolor.green
            return

        if colorspec[:7] == "random(":
            l = colorspec[7:-1]
            comp = ""
            value = ""
            if l[0] in _COMPS:
                comp = l[0]
                start = 1
                if l[1] in _COMPS:
                    comp = comp + l[1]
                    start = 2
                value = l[start:]
            else:
                value = l

            try:
                somecolor = self.randcolor(int(value))
            except ValueError:
                raise BadColorSpecError(colorspec)

            self.red = somecolor.red
            self.blue = somecolor.blue
            self.green = somecolor.green
            return

        ####randhue
        if colorspec[:8] == "randhue(":
            parms = colorspec[8:-1].split(",", 1)
            saturation, brightness = float(parms[0]), float(parms[1])
            somecolor = self.randhue(saturation, brightness)
            self.red, self.blue, self.green = (
                somecolor.red,
                somecolor.blue,
                somecolor.green,
            )
            return

        ####rrggbb
        if len(colorspec) in [6, 7]:
            triplet = colorspec
            if triplet[0] == "#":
                triplet = triplet[1:]
            self.red = int("%s" % triplet[0:2], 16)
            self.green = int("%s" % triplet[2:4], 16)
            self.blue = int("%s" % triplet[4:6], 16)
            return

        ####rgb
        if re.match(r"#[0-9,[A-F]{3}$", colorspec, re.I):
            self.red = int(colorspec[1], 16) * 17
            self.green = int(colorspec[2], 16) * 17
            self.blue = int(colorspec[3], 16) * 17
            return

        raise BadColorSpecError(repr(colorspec))

    def __repr__(self) -> str:
        return "#%02x%02x%02x" % (self.red, self.green, self.blue)

    def __add__(self, value: Union["Color", float]) -> "Color":
        if isinstance(value, (int, float)):
            red = self.red + value
            blue = self.blue + value
            green = self.green + value

            red, green, blue = [
                self._sanitize(component) for component in (red, green, blue)
            ]

            return Color((red, green, blue))

        return Color(
            (self.red + value.red, self.blue + value.blue, self.green + value.green)
        )

    def __mul__(self, value: Union["Color", float]) -> "Color":
        """This should be used instead of __add__ as it makes more sense"""

        if isinstance(value, (int, float)):
            red = self.red * value
            green = self.green * value
            blue = self.blue * value

            red, green, blue = [self._sanitize(i) for i in (red, green, blue)]

            return Color((red, green, blue))

        clum = value.luminocity()
        return self * clum

    __rmul__ = __mul__

    def __div__(self, value: Union["Color", float]) -> "Color":
        """Just like __mul__"""

        if isinstance(value, (int, float)):
            return self * (1.0 / value)

        clum = value.luminocity()
        return self / clum

    def __sub__(self, value: Union["Color", float]) -> "Color":
        return self.__add__(-value)

    def _sanitize(self, number: float) -> int:
        """Make sure 0 <= number <= 255"""
        number = min(255, number)
        number = max(0, number)

        return int(number)

    def colorify(self, color: "Color", fix_bw: bool = True) -> "Color":
        """Return new color with color's hue and self's saturation and value"""
        # black and white don't make good HSV values, so we make them
        # imperfect
        if fix_bw and self == Color("white"):
            my_color = Color((254, 254, 254))
        elif fix_bw and self == Color("black"):
            my_color = Color((1, 1, 1))
        else:
            my_color = Color(self)

        my_hsv = my_color.toHSV()
        color_hsv = color.toHSV()

        new_color = Color.fromHSV((color_hsv[0], my_hsv[1], my_hsv[2]))
        return new_color

    @classmethod
    def randcolor(cls, l: Optional[float] = None, comp: str = "=") -> "Color":
        """Return random color color.luminocity() = l """

        low_range = 0
        high_range = 255
        ops = {
            "<": operator.lt,
            "<=": operator.le,
            "=": operator.eq,
            ">": operator.gt,
            ">=": operator.ge,
        }
        randint = random.randint

        color = cls(
            (
                randint(low_range, high_range),
                randint(low_range, high_range),
                randint(low_range, high_range),
            )
        )

        if not l:
            return color

        try:
            op = ops[comp]
        except KeyError:
            raise BadColorSpecError("random(%s%s)" % (comp, l))

        while True:
            if op(color.luminocity(), l):
                return color

            color = cls(
                (
                    randint(low_range, high_range),
                    randint(low_range, high_range),
                    randint(low_range, high_range),
                )
            )

    def inverse(self) -> "Color":
        """Return inverse of color"""

        return Color((255 - self.red, 255 - self.green, 255 - self.blue))

    def winverse(self) -> "Color":
        """Keep red part, change green to 255-, change blue to 0"""

        return Color((self.red // 2, 255 - self.green, 0))

    def to_gtk(self) -> str:
        """return string of Color in gtkrc format"""
        return "{ %.2f, %.2f, %.2f }" % (
            self.red / 255.0,
            self.green / 255.0,
            self.blue / 255.0,
        )

    def luminocity(self) -> float:
        """Return (int) luminocity of color"""
        # from http://tinyurl.com/8cve8
        return int(round(0.30 * self.red + 0.59 * self.green + 0.11 * self.blue))

    def pastelize(self) -> "Color":
        """Return a "pastel" version of self"""
        hsv = self.toHSV()

        return self.fromHSV((hsv[0], self.PASTEL_SATURATION, self.PASTEL_BRIGHTNESS))

    @classmethod
    def gradient(cls, from_color: "Color", to_color: "Color", steps: int):
        """Generator for creating gradients"""
        yield from_color

        fsteps = float(steps - 1)
        inc_red = (to_color.red - from_color.red) / fsteps
        inc_green = (to_color.green - from_color.green) / fsteps
        inc_blue = (to_color.blue - from_color.blue) / fsteps

        new_red = float(from_color.red)
        new_blue = float(from_color.blue)
        new_green = float(from_color.green)

        for _ in range(steps - 2):  # minus the 2 endpoints
            new_red = new_red + inc_red
            new_green = new_green + inc_green
            new_blue = new_blue + inc_blue
            new_color = cls((int(new_red), int(new_green), int(new_blue)))
            yield new_color

        yield to_color

    def factor_tuple(self, mytuple) -> "Color":
        """Same as factor_int, but multiply by a 3-tuple
        Return normalized color
        """

        red = min(self.red * mytuple[0], 255)
        green = min(self.green * mytuple[1], 255)
        blue = min(self.blue * mytuple[2], 255)

        # Guess we should check for negative values too
        red = int(max(red, 0))
        green = int(max(green, 0))
        blue = int(max(blue, 0))

        return Color((red, green, blue))

    def factor(self, myint) -> "Color":
        """Same as factor_tuple, but just one number"""

        return self.factor_tuple((myint, myint, myint))

    @classmethod
    def randhue(cls, saturation, brightness) -> "Color":
        """Create color with random hue based on saturation and brightness"""
        saturation = float(saturation)
        brightness = float(brightness)
        hue = random.randint(0, 360)
        return Color.fromHSV((hue, saturation, brightness))

    def toHSV(self) -> Tuple[float, float, float]:
        """Return a tuple containing (Hue, Saturation, Value)"""

        r, g, b = self.red / 255.0, self.green / 255.0, self.blue / 255.0
        minimum = min(r, g, b)
        maximum = max(r, g, b)
        v = maximum
        delta = maximum - minimum

        if maximum != 0.0:
            s = delta / maximum
        else:
            s = 0.0
        if s == 0.0:
            h = -1.0
        else:
            if r == maximum:
                h = (g - b) / delta
            elif g == maximum:
                h = 2 + (b - r) / delta
            elif b == maximum:
                h = 4 + (r - g) / delta
            h = h * 60.0
            if h < 0:
                h = h + 360.0
        return (h, s * 100.0, v * 100.0)

    @classmethod
    def fromHSV(cls, HSV: Tuple[float, float, float]) -> "Color":
        """Create a color from HSV value (tuple)"""
        from math import floor

        h, s, v = HSV[0] / 360.0, HSV[1] / 100.0, HSV[2] / 100.0
        if h < 0.0:
            h = 0.5
        if s == 0.0:  # grayscale
            r = g = b = v
        else:
            if h == 1.0:
                h = 0
            h = h * 6.0
            i = floor(h)
            f = h - i
            aa = v * (1 - s)
            bb = v * (1 - (s * f))
            cc = v * (1 - (s * (1 - f)))
            if i == 0:
                r, g, b = v, cc, aa
            elif i == 1:
                r, g, b = bb, v, aa
            elif i == 2:
                r, g, b = aa, v, cc
            elif i == 3:
                r, g, b = aa, bb, v
            elif i == 4:
                r, g, b = cc, aa, v
            elif i == 5:
                r, g, b = v, aa, bb

        return cls((int(r * 255), int(g * 255), int(b * 255)))

    # TODO: consider replacing with webcolors: https://pypi.org/project/webcolors/
    @classmethod
    def load_rgb(cls):
        for line in open(cls.RGB_FILENAME, "r"):
            line = line.strip()

            if not line or line[0] == "!":
                continue

            fields = line.split(None, 3)

            try:
                color_t = tuple([int(i) for i in fields[:3]])
                color_name = fields[3]
                cls.rgb[color_name.lower()] = color_t
            except ValueError:
                continue


def parse_args(args: tuple) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("--input", "-i", default=None)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--fuzz", "-f", type=int, default=0)
    parser.add_argument("--interval", "-n", type=int, default=INTERVAL)
    parser.add_argument("output", type=str)

    return parser.parse_args(args)


def read_file(filename: str) -> str:
    pipe_exec = filename.startswith("!")

    if pipe_exec:
        popen = subprocess.Popen(
            os.path.expanduser(filename[1:]), shell=True, stdout=subprocess.PIPE
        )
        content = popen.stdout.read().decode()
    else:
        with open(os.path.expanduser(filename), "r") as myfile:
            content = myfile.read()

    return content


def write_file(filename: str, text: str) -> int:
    """write open *filename* and write *text* to it"""
    with open(filename, "w") as myfile:
        return myfile.write(text)


async def watch_file(watcher, loop, handler):
    try:
        await watcher.setup(loop)
    except OSError as error:
        LOGGER.warn(error)

        return

    while True:
        await watcher.get_event()
        handler()


def randsign(num: int) -> int:
    return random.choice([-1, 1]) * random.randint(0, num)


def run(reload_config: bool = False) -> None:
    if reload_config:
        CONFIG.read(CONFIG_PATH)

    orig_svg = read_file(os.path.expanduser(CONFIG["larry"]["input"]))
    orig_colors = list(get_colors(orig_svg))
    orig_colors.sort(key=Color.luminocity)
    orig_colors = [i for i in orig_colors if i.luminocity() not in (0, 255)]
    fuzz = CONFIG.getint("larry", "fuzz")
    lum1 = max([orig_colors[0].luminocity() + randsign(fuzz), 1])
    lum2 = min([orig_colors[-1].luminocity() + randsign(fuzz), 254])
    svg = orig_svg
    colors_str = CONFIG["larry"].get("colors", "").strip().split()

    if colors_str:
        LOGGER.debug("using colors from config")
        colors = [Color(i.strip()) for i in colors_str]
    else:
        colors = Color.gradient(
            Color.randcolor(l=lum1), Color.randcolor(l=lum2), len(orig_colors)
        )
        colors = list(colors)

    LOGGER.debug("new colors: %s", colors)

    for orig, new in zip(orig_colors, colors):
        color_str = str(new)
        svg = svg.replace(orig.colorspec, color_str)

    outfile = CONFIG["larry"]["output"]
    write_file(outfile, svg)

    # now run any plugins
    if "larry" not in CONFIG.sections():
        return

    plugins = CONFIG["larry"].get("plugins", "").split()
    loop = asyncio.get_event_loop()

    for plugin_name in plugins:
        loop.call_soon(do_plugin, plugin_name, colors)


def do_plugin(plugin_name: str, colors: List[Color]) -> None:
    plugin = load_plugin(plugin_name)
    config = get_plugin_config(plugin_name)

    LOGGER.debug("Running plugin for %s", plugin_name)
    plugin(colors, config)


def get_plugin_config(plugin_name: str) -> ConfigType:
    plugin_config_name = f"plugins:{plugin_name}"

    if plugin_config_name in CONFIG:
        plugin_config = dict(CONFIG[plugin_config_name])
    else:
        plugin_config = {}

    return plugin_config


def load_plugin(name: str):
    if name not in PLUGINS:
        iter_ = pkg_resources.iter_entry_points("larry.plugins", name)
        plugin = next(iter_).load()
        PLUGINS[name] = plugin

    return PLUGINS[name]


def run_every(interval: float, loop, reload_config: bool = False) -> None:
    """Run *callback* immediately and then every *interval* seconds after"""
    global HANDLER

    if HANDLER:
        LOGGER.warning("received signal to change wallpaper")
        HANDLER.cancel()

    run(reload_config)

    if interval == 0:
        return

    HANDLER = loop.call_later(interval, run_every, interval, loop)


def get_colors(svg: str) -> Set[Color]:
    color_strings = {i for i in COLOR_RE.findall(svg)}

    return {Color(i) for i in color_strings}


def rrggbb(color: str, theme_color: Color, css: str) -> str:
    color = "#" + color
    orig_color = Color(color)
    new_color = orig_color.colorify(theme_color)

    return re.sub(str(color), str(new_color), css, flags=re.I)


def rgb(color: str, theme_color: Color, css: str) -> str:
    red, green, blue = [int(float(i)) for i in color.split(",")]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape(f"rgb({color})")

    return re.sub(re_str, str(new_color), css, flags=re.I)


def rgba(color: str, theme_color: Color, css: str) -> str:
    parts = color.split(",")
    red, green, blue, *_ = [int(float(i)) for i in parts]
    orig_color = Color((red, green, blue))
    new_color = orig_color.colorify(theme_color)
    re_str = re.escape("rgba({},{},{},".format(*parts[:3]))
    re_str = re_str + r"(" + re.escape(parts[-1]) + r")\)"
    new_str = "rgba({},{},{},\\1)".format(
        new_color.red, new_color.green, new_color.blue
    )

    return re.sub(re_str, new_str, css, flags=re.I)


def init_config():
    if "larry" not in CONFIG:
        CONFIG["larry"] = {}


def main(args=None):
    """Main program entry point"""
    init_config()
    args = parse_args(args or sys.argv[1:])

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    LOGGER.debug("args=%s", args)

    if args.input:
        CONFIG["larry"]["input"] = args.input

    if args.fuzz is not None:
        CONFIG["larry"]["fuzz"] = str(args.fuzz)

    CONFIG["larry"]["output"] = args.output

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGUSR1, run_every, args.interval, loop, True)
    loop.call_soon(run_every, args.interval, loop)

    watcher = aionotify.Watcher()
    watcher.watch(CONFIG_PATH, aionotify.Flags.MODIFY | aionotify.Flags.CREATE)
    loop.create_task(
        watch_file(
            watcher, loop, functools.partial(run_every, args.interval, loop, True)
        )
    )

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        LOGGER.info("User interrupted")
        loop.stop()
    finally:
        loop.close()


if __name__ == "__main__":
    main()
