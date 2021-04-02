"""The ubiquitous Color class"""
from __future__ import annotations

import random
import re
from math import floor
from typing import Generator, List, Optional, Tuple, Union

ColorSpecType = Union[str, "Color", Tuple[int, int, int]]

_COMPS = (">", "<", "=")


def color_names(filename):
    """Load the rgb.txt name-to-value file"""
    rgb = {}

    try:
        rgbfile = open(filename, "r")
    except FileNotFoundError:
        return rgb

    with rgbfile:
        for line in rgbfile:
            line = line.strip()

            if not line or line[0] == "!":
                continue

            fields = line.split(None, 3)

            try:
                color_t = tuple(int(i) for i in fields[:3])
                color_name = fields[3]
                rgb[color_name.lower()] = color_t
            except ValueError:
                continue

    return rgb


class BadColorSpecError(ValueError):
    """Exception when an invalid spec was passed to the Color initializer"""


# The following class was written a *long* time ago in Python 2.x and
# was in a different package. It was hastily ported here and either
# needs to be cleaned up or replaced with a different package.
class Color:
    """tuple-like color class"""

    PASTEL_SATURATION = 50
    PASTEL_BRIGHTNESS = 100
    RGB_FILENAME = "/usr/share/X11/rgb.txt"
    names = color_names(RGB_FILENAME)

    def __init__(self, colorspec: ColorSpecType = "random") -> None:
        self.colorspec = colorspec

        ####(r, g , b)
        if isinstance(colorspec, (tuple, list)):
            self.__rgb = tuple(int(i) for i in colorspec)

        elif isinstance(colorspec, Color):
            # copy color
            self.__rgb = colorspec.rgb
            return

        elif isinstance(colorspec, str):
            self.__rgb = self._handle_str_colorspec(colorspec)

        else:
            raise BadColorSpecError(repr(colorspec))

    @property
    def red(self):
        """Red value"""
        return self.__rgb[0]

    @property
    def green(self):
        """Green value"""
        return self.__rgb[1]

    @property
    def blue(self):
        """Blue value"""
        return self.__rgb[2]

    @property
    def rgb(self):
        """Return color as an (r, g, b) tuple"""
        return self.__rgb

    def __eq__(self, other):
        return self.rgb == other.rgb

    def __hash__(self):
        return hash(self.__rgb)

    def _handle_str_colorspec(self, colorspec: str):
        """Handle *colorspec* of type str"""
        colorspec = colorspec.strip('"')

        ###rbg(r, g, b)
        if colorspec.startswith("rgb("):
            parts = colorspec[4:-2].split(",")
            return tuple(int(i.strip()) for i in parts)

        ####r/g/b
        if len(colorspec.split("/")) == 3:
            parts = colorspec.split("/")
            return tuple(int(i) for i in parts)

        ####{ r, g, b}
        if colorspec[0] == "{" and colorspec[-1] == "}":
            red, green, blue = colorspec[1:-1].split(",")
            return (
                int(float(red) * 255),
                int(float(green) * 255),
                int(float(blue) * 255),
            )

        if val := self.names.get(colorspec.lower()):
            return val

        ####random
        if colorspec == "random":
            return self.randcolor().rgb

        if colorspec[:7] == "random(":
            lum = colorspec[7:-1]
            comp = ""
            value = ""
            if lum[0] in _COMPS:
                comp = lum[0]
                start = 1
                if lum[1] in _COMPS:
                    comp = comp + lum[1]
                    start = 2
                value = lum[start:]
            else:
                value = lum

            try:
                somecolor = self.randcolor(int(value))
            except ValueError as error:
                raise BadColorSpecError(colorspec) from error

            return somecolor.rgb

        ####randhue
        if colorspec[:8] == "randhue(":
            parms = colorspec[8:-1].split(",", 1)
            saturation, brightness = float(parms[0]), float(parms[1])

            return self.randhue(saturation, brightness).rgb

        ####rrggbb
        if len(colorspec) in [6, 7]:
            triplet = colorspec
            if triplet[0] == "#":
                triplet = triplet[1:]
            return (
                int("%s" % triplet[0:2], 16),
                int("%s" % triplet[2:4], 16),
                int("%s" % triplet[4:6], 16),
            )

        ####rgb
        if re.match(r"#[0-9,[A-F]{3}$", colorspec, re.I):
            return (
                int(colorspec[1], 16) * 17,
                int(colorspec[2], 16) * 17,
                int(colorspec[3], 16) * 17,
            )

        raise BadColorSpecError(repr(colorspec))

    def __str__(self) -> str:
        return "#%02x%02x%02x" % self.__rgb

    def __repr__(self) -> str:
        name = type(self).__name__
        return f"{name}({self.__rgb})"

    def __add__(self, value: Union[Color, float]) -> Color:
        if isinstance(value, (int, float)):
            red = self.red + value
            blue = self.blue + value
            green = self.green + value

            red, green, blue = [sanitize(component) for component in (red, green, blue)]

            return Color((red, green, blue))

        return Color(
            (
                sanitize(self.red + value.red),
                sanitize(self.blue + value.blue),
                sanitize(self.green + value.green),
            )
        )

    def __mul__(self, value: Union[Color, float]) -> Color:
        """This should be used instead of __add__ as it makes more sense"""

        if isinstance(value, (int, float)):
            red = self.red * value
            green = self.green * value
            blue = self.blue * value

            red, green, blue = [sanitize(i) for i in (red, green, blue)]

            return Color((red, green, blue))

        clum = value.luminocity()
        return self * clum

    __rmul__ = __mul__

    def __div__(self, value: Union[Color, float]) -> Color:
        """Just like __mul__"""

        if isinstance(value, (int, float)):
            return self * (1.0 / value)

        clum = value.luminocity()

        return self * (1 / clum)

    def __sub__(self, value: Union[Color, float]) -> Color:
        return self.__add__(-1 * value)

    def colorify(self, color: Color, fix_bw: bool = False) -> Color:
        """Return new color with color's hue and self's saturation and value"""
        # black and white don't make good HSV values, so we make them
        # imperfect
        if fix_bw and self == Color((255, 255, 255)):
            my_color = Color((254, 254, 254))
        elif fix_bw and self == Color((0, 0, 0)):
            my_color = Color((1, 1, 1))
        else:
            my_color = Color(self)

        my_hsv = my_color.to_hsv()
        color_hsv = color.to_hsv()

        new_color = Color.from_hsv((color_hsv[0], my_hsv[1], my_hsv[2]))
        return new_color

    @classmethod
    def randcolor(cls, lum: Optional[float] = None, comp: str = "=") -> Color:
        """Return random color color.luminocity() = lum"""
        randint = random.randint
        color = cls(
            (
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
            )
        )

        if not lum:
            return color

        lum = int(lum)

        if comp == "=":
            pass
        elif comp == "<":
            lum = randint(0, lum - 1)
        elif comp == "<=":
            lum = randint(0, lum)
        elif comp == ">":
            lum = randint(lum + 1, 255)
        elif comp == ">=":
            lum = randint(lum, 255)
        else:
            raise BadColorSpecError("random(%s%s)" % (comp, lum))

        return color.luminize(lum)

    def inverse(self) -> Color:
        """Return inverse of color"""

        return Color((255 - self.red, 255 - self.green, 255 - self.blue))

    def winverse(self) -> Color:
        """Keep red part, change green to 255-, change blue to 0"""

        return Color((self.red // 2, 255 - self.green, 0))

    def to_gtk(self) -> str:
        """return string of Color in gtkrc format"""
        return "{ %.2f, %.2f, %.2f }" % (
            self.red / 255.0,
            self.green / 255.0,
            self.blue / 255.0,
        )

    def to_ansi256(self) -> int:
        """Return color's approximate equivalent in the ANSI 256-color pallette"""
        if self.red == self.green and self.green == self.blue:
            if self.red < 8:
                return 16
            if self.red > 248:
                return 231

            return round(((self.red - 8) / 247.0) * 24) + 232

        ansi_red = 36 * round(self.red / 255.0 * 5.0)
        ansi_green = 6 * round(self.green / 255.0 * 5.0)
        ansi_blue = round(self.blue / 255.0 * 5.0)
        ansi = 16 + ansi_red + ansi_green + ansi_blue

        return ansi

    def luminocity(self) -> float:
        """Return (int) luminocity of color"""
        # from http://tinyurl.com/8cve8
        return int(round(0.30 * self.red + 0.59 * self.green + 0.11 * self.blue))

    def pastelize(self) -> Color:
        """Return a "pastel" version of self"""
        hsv = self.to_hsv()

        return self.from_hsv((hsv[0], self.PASTEL_SATURATION, self.PASTEL_BRIGHTNESS))

    def luminize(self, luminocity: float) -> Color:
        """Return new color with given luminocity

        E.g.::

            >>> print(Color("#a4c875").luminize(40))
            #242c1a
        """
        my_lum = self.luminocity()

        if my_lum == 0.0:
            # black
            value = int(luminocity)
            return type(self)((value, value, value))

        lum = (luminocity - my_lum) / my_lum
        parts = [*self.rgb]

        for i in range(3):
            part = parts[i]
            part = round(min(max(0, part + (part * lum)), 255))
            parts[i] = part

        return type(self)(tuple(parts))

    @classmethod
    def gradient(cls, from_color: Color, to_color: Color, steps: int) -> ColorGenerator:
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

    @classmethod
    def generate_from(
        cls, colors: ColorList, needed: int, randomize=True
    ) -> ColorGenerator:
        """return exactly needed colors"""
        if needed < 0:
            raise ValueError("needed argument must be non-negative", needed)

        num_colors = len(colors)

        if not num_colors:
            yield from (Color.randcolor() for _ in range(needed))
            return

        # If the number of colors is the number requested, return those colors shuffled
        if num_colors == needed:
            if randomize:
                random.shuffle(colors)
            yield from colors
            return

        # If we don't have any colors (left), return a random selection
        if num_colors == 0:
            yield from (cls() for _ in range(needed))
            return

        # If the number needed is less than the number available, return a random sample
        if needed < num_colors:
            yield from random.sample(colors, needed)
            return

        # If there are only 2 available colors, return a gradient from darkest to lightest
        if num_colors == 2:
            colors.sort(key=Color.luminocity)
            yield from Color.gradient(colors[0], colors[1], needed)
            return

        # Split the colors in half
        split = needed // 2

        yield from cls.generate_from(colors[:split], split)
        yield from cls.generate_from(colors[split:], needed - split)

    def factor_tuple(self, mytuple) -> Color:
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

    def factor(self, myint) -> Color:
        """Same as factor_tuple, but just one number"""

        return self.factor_tuple((myint, myint, myint))

    @classmethod
    def randhue(cls, saturation, brightness) -> Color:
        """Create color with random hue based on saturation and brightness"""
        saturation = float(saturation)
        brightness = float(brightness)
        hue = random.randint(0, 360)
        return Color.from_hsv((hue, saturation, brightness))

    def to_hsv(self) -> Tuple[float, float, float]:
        """Return a tuple containing (Hue, Saturation, Value)"""

        red, green, blue = self.red / 255.0, self.green / 255.0, self.blue / 255.0
        minimum = min(red, green, blue)
        maximum = max(red, green, blue)
        value = maximum
        delta = maximum - minimum

        if maximum != 0.0:
            saturation = delta / maximum
        else:
            saturation = 0.0
        if saturation == 0.0:
            hue = -1.0
        else:
            if red == maximum:
                hue = (green - blue) / delta
            elif green == maximum:
                hue = 2 + (blue - red) / delta
            elif blue == maximum:
                hue = 4 + (red - green) / delta
            hue = hue * 60.0
            if hue < 0:
                hue = hue + 360.0
        return (hue, saturation * 100.0, value * 100.0)

    @classmethod
    def from_hsv(cls, hsv: Tuple[float, float, float]) -> Color:
        """Create a color from HSV value (tuple)"""

        hue, saturation, value = hsv[0] / 360.0, hsv[1] / 100.0, hsv[2] / 100.0
        if hue < 0.0:
            hue = 0.5
        if saturation == 0.0:  # grayscale
            red = green = blue = value
        else:
            if hue == 1.0:
                hue = 0
            hue = hue * 6.0
            i = floor(hue)
            f = hue - i
            aa = value * (1 - saturation)
            bb = value * (1 - (saturation * f))
            cc = value * (1 - (saturation * (1 - f)))
            if i == 0:
                red, green, blue = value, cc, aa
            elif i == 1:
                red, green, blue = bb, value, aa
            elif i == 2:
                red, green, blue = aa, value, cc
            elif i == 3:
                red, green, blue = aa, bb, value
            elif i == 4:
                red, green, blue = cc, aa, value
            elif i == 5:
                red, green, blue = value, aa, bb

        return cls((int(red * 255), int(green * 255), int(blue * 255)))


ColorList = List[Color]
ColorGenerator = Generator[Color, None, None]


def sanitize(number: float) -> int:
    """Make sure 0 <= number <= 255"""
    number = min(255, number)
    number = max(0, number)

    return int(number)


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
