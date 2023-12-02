"""The ubiquitous Color class"""
from __future__ import annotations

import random
import re
from collections import namedtuple
from dataclasses import dataclass
from math import floor
from typing import Iterator, Optional, TypeAlias, TypeGuard, TypeVar, Union

ColorSpecType: TypeAlias = Union[str, "Color", tuple[int, int, int]]

_COMPS = (">", "<", "=")

# (default) values for Color.pastelize
PASTEL_SATURATION = 50
PASTEL_BRIGHTNESS = 100


class BadColorSpecError(ValueError):
    """Exception when an invalid spec was passed to the Color initializer"""


class Color(namedtuple("Color", ["red", "green", "blue"])):
    """tuple-like color class"""

    __slots__ = ()

    def __new__(cls, *colorspec) -> Color:
        # self.colorspec = colorspec

        if not colorspec:
            colorspec = ("random",)

        ####(r, g , b)
        if len(colorspec) == 3:
            for value in colorspec:
                if not 0 <= value <= 255:
                    raise ValueError("All values must be in range [0, 255]")

            return super().__new__(cls, *colorspec)

        if len(colorspec) != 1:
            raise BadColorSpecError(repr(colorspec))

        if isinstance(colorspec[0], Color):
            # copy color
            return super().__new__(
                cls, colorspec[0].red, colorspec[0].green, colorspec[0].blue
            )
        if isinstance(colorspec[0], str):
            return super().__new__(cls, *cls._handle_str_colorspec(colorspec[0]))

        raise BadColorSpecError(repr(colorspec))

    @classmethod
    def _handle_str_colorspec(cls, color_str: str) -> tuple[int, int, int]:
        """Handle *colorspec* of type str"""
        from larry.names import NAMES  # pylint: disable=import-outside-toplevel

        color_str = color_str.strip('"')

        ###rbg(r, g, b)
        if color_str.startswith("rgb("):
            red, green, blue = color_str[4:-2].split(",")
            return int(red.strip()), int(blue.strip()), int(green.strip())

        ####r/g/b
        if len(color_str.split("/")) == 3:
            red, green, blue = color_str.split("/")
            return int(red), int(green), int(blue)

        ####{ r, g, b}
        if color_str[0] == "{" and color_str[-1] == "}":
            red, green, blue = color_str[1:-1].split(",")
            return (
                int(float(red) * 255),
                int(float(green) * 255),
                int(float(blue) * 255),
            )

        if val := NAMES.get(color_str.lower()):
            return val

        ####random
        if color_str == "random":
            return cls.randcolor()

        if color_str[:7] == "random(":
            lum = color_str[7:-1]
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
                somecolor = cls.randcolor(int(value))
            except ValueError as error:
                raise BadColorSpecError(color_str) from error

            return somecolor

        ####randhue
        if color_str[:8] == "randhue(":
            params = color_str[8:-1].split(",", 1)
            saturation, brightness = float(params[0]), float(params[1])

            return cls.randhue(saturation, brightness)

        ####rrggbb
        if len(color_str) in [3, 4]:
            triplet = color_str
            if triplet[0] == "#":
                triplet = triplet[1:]
            return (
                int(triplet[0] * 2, 16),
                int(triplet[1] * 2, 16),
                int(triplet[2] * 2, 16),
            )
        if len(color_str) in [6, 7]:
            triplet = color_str
            if triplet[0] == "#":
                triplet = triplet[1:]
            return (
                int(triplet[0:2], 16),
                int(triplet[2:4], 16),
                int(triplet[4:6], 16),
            )

        ####rgb
        if re.match(r"#[0-9,[A-F]{3}$", color_str, re.I):
            return (
                int(color_str[1], 16) * 17,
                int(color_str[2], 16) * 17,
                int(color_str[3], 16) * 17,
            )

        raise BadColorSpecError(repr(color_str))

    def __str__(self) -> str:
        return f"#{self.red:02x}{self.green:02x}{self.blue:02x}"

    def __add__(self, value: Color | float) -> Color:
        if isinstance(value, (int, float)):
            red = self.red + value
            blue = self.blue + value
            green = self.green + value

            red, green, blue = [sanitize(component) for component in (red, green, blue)]

            return Color(red, green, blue)

        return Color(
            sanitize(self.red + value.red),
            sanitize(self.blue + value.blue),
            sanitize(self.green + value.green),
        )

    def __mul__(self, value: Color | float) -> Color:
        """This should be used instead of __add__ as it makes more sense"""

        if isinstance(value, (int, float)):
            red = self.red * value
            green = self.green * value
            blue = self.blue * value

            red, green, blue = [sanitize(i) for i in (red, green, blue)]

            return Color(red, green, blue)

        clum = value.luminocity()
        return self * clum

    __rmul__ = __mul__

    def __div__(self, value: Color | float) -> Color:
        """Just like __mul__"""

        if isinstance(value, (int, float)):
            return self * (1.0 / value)

        clum = value.luminocity()

        return self * (1 / clum)

    def __sub__(self, value: Color | float) -> Color:
        return self.__add__(-1 * value)

    def colorify(self, color: Color, fix_bw: bool = False) -> Color:
        """Return new color with color's hue and self's saturation and value"""
        # black and white don't make good HSV values, so we make them
        # imperfect
        if fix_bw and self == Color(255, 255, 255):
            my_color = Color(254, 254, 254)
        elif fix_bw and self == Color(0, 0, 0):
            my_color = Color(1, 1, 1)
        else:
            my_color = Color(*self)

        my_hsv = my_color.to_hsv()
        color_hsv = color.to_hsv()

        new_color = Color.from_hsv((color_hsv[0], my_hsv[1], my_hsv[2]))
        return new_color

    @classmethod
    def randcolor(cls, lum: Optional[float] = None, comp: str = "=") -> Color:
        """Return random color color.luminocity() = lum"""
        randint = random.randint
        color = cls(randint(0, 255), randint(0, 255), randint(0, 255))

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
            raise BadColorSpecError(f"random({comp}{lum})")

        return color.luminize(lum)

    def inverse(self) -> Color:
        """Return inverse of color"""

        return Color(255 - self.red, 255 - self.green, 255 - self.blue)

    def winverse(self) -> Color:
        """Keep red part, change green to 255-, change blue to 0"""

        return Color(self.red // 2, 255 - self.green, 0)

    def to_gtk(self) -> str:
        """return string of Color in gtkrc format"""
        return f"{self.red / 255:.2f}, {self.green / 255:.2f}, {self.blue / 255:.2f}"

    def to_ansi256(self) -> int:
        """Return color's approximate equivalent in the ANSI 256-color palette"""
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

    def luminocity(self) -> int:
        """Return (int) luminocity of color"""
        # from http://tinyurl.com/8cve8
        return int(round(0.30 * self.red + 0.59 * self.green + 0.11 * self.blue))

    def pastelize(
        self, *, saturation: Optional[int] = None, brightness: Optional[int] = None
    ) -> Color:
        """Return a "pastel" version of self"""
        if saturation is None:
            saturation = PASTEL_SATURATION

        if brightness is None:
            brightness = PASTEL_BRIGHTNESS

        hsv = self.to_hsv()

        return self.from_hsv((hsv[0], saturation, brightness))

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
            return type(self)(value, value, value)

        lum = (luminocity - my_lum) / my_lum
        parts = [*self]

        for i in range(3):
            part = parts[i]
            part = round(min(max(0, part + (part * lum)), 255))
            parts[i] = part

        return type(self)(*parts)

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
            new_color = cls(int(new_red), int(new_green), int(new_blue))
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

        # If there are only 2 available colors, return a gradient from darkest to
        # lightest
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

        return Color(red, green, blue)

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

    def to_hsv(self) -> tuple[float, float, float]:
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
    def from_hsv(cls, hsv: tuple[float, float, float]) -> Color:
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

        return cls(int(red * 255), int(green * 255), int(blue * 255))


ColorList: TypeAlias = list[Color]
ColorGenerator: TypeAlias = Iterator[Color]


def between_0_and_1(value: float) -> TypeGuard[float]:
    """Return true if value is between 0 and 1 (inclusive)"""
    return 0 <= value <= 1


ColorFloatType = TypeVar("ColorFloatType", bound="ColorFloat")


@dataclass(frozen=True)
class ColorFloat:
    """Like Color but a quadruplet of floats [0..1]"""

    red: float = 0.0
    green: float = 0.0
    blue: float = 0.0
    alpha: float = 1.0

    def __post_init__(self) -> None:
        if not between_0_and_1(self.red):
            raise ValueError("red must be between 0 and 1")
        if not between_0_and_1(self.green):
            raise ValueError("green must be between 0 and 1")
        if not between_0_and_1(self.blue):
            raise ValueError("blue must be between 0 and 1")
        if not between_0_and_1(self.alpha):
            raise ValueError("alpha must be between 0 and 1")

    @classmethod
    def from_color(
        cls: type[ColorFloatType], color: Color, opacity: float = 1.0
    ) -> ColorFloatType:
        """Return ColorFloat given Color.

        If opacity is passed, the ColorFloat will have the given color. Otherwise it
        defaults to 1.0
        """
        return cls(color.red / 255, color.green / 255, color.blue / 255, opacity)

    def to_color(self) -> Color:
        """Convert ColorFloat to a Color

        Opacity information will be lost
        """
        return Color(int(self.red * 255), int(self.green * 255), int(self.blue * 255))

    def __bool__(self) -> bool:
        if self.red + self.green + self.blue:
            return True

        return False


def sanitize(number: float) -> int:
    """Make sure 0 <= number <= 255"""
    number = min(255, number)
    number = max(0, number)

    return int(number)


def replace_string(string: str, color_str: str, color: Color) -> str:
    """Replace each occurrence of color_str in string with this color

    Where `color_str` is one of the following formats:

        * rrggbb   e.g. "ffc0cb"
        * r,g,b    e.g. "255,192,203"
        * r,g,b,a  e.g. "255,192,203,0.8"
    """
    num_commas = color_str.count(",")

    if num_commas == 0:
        # rrggbb
        string = rrggbb(color_str, color, string)
    elif num_commas == 2:
        # r,g,b
        string = rgb(color_str, color, string)
    elif num_commas == 3:
        # r,g,b,a
        string = rgba(color_str, color, string)

    return string


def rrggbb(color_str: str, color: Color, string: str) -> str:
    color_str = "#" + color_str
    orig_color = Color(color_str)
    new_color = orig_color.colorify(color)

    return re.sub(str(color_str), str(new_color), string, flags=re.I)


def rgb(color_str: str, color: Color, string: str) -> str:
    red, green, blue = [int(float(i)) for i in color_str.split(",")]
    orig_color = Color(red, green, blue)
    new_color = orig_color.colorify(color)
    re_str = re.escape(f"rgb\\({red}, *{green}, *{blue}\\)")

    return re.sub(re_str, str(new_color), string, flags=re.I)


def rgba(color_str: str, color: Color, string: str) -> str:
    parts = color_str.split(",")
    red, green, blue, *_ = [int(float(i)) for i in parts]
    orig_color = Color(red, green, blue)
    new_color = orig_color.colorify(color)
    re_str = f"rgba\\({parts[0]}, *{parts[1]}, *{parts[2]}, *"
    re_str = re_str + r"(" + re.escape(parts[-1]) + r")\)"
    new_str = f"rgba({new_color.red}, {new_color.green}, {new_color.blue}, \\1)"

    return re.sub(re_str, new_str, string, flags=re.I)


def combine(fg: ColorFloat, bg: ColorFloat) -> ColorFloat:
    """Combine two ColorFloats"""
    # https://stackoverflow.com/questions/726549/algorithm-for-additive-color-mixing-for-rgb-values
    alpha = 1 - (1 - fg.alpha) * (1 - bg.alpha)

    if alpha < 1.0e-6:
        return ColorFloat(alpha=0)

    red = fg.red * fg.alpha / alpha + bg.red * bg.alpha * (1 - fg.alpha) / alpha
    green = fg.green * fg.alpha / alpha + bg.green * bg.alpha * (1 - fg.alpha) / alpha
    blue = fg.blue * fg.alpha / alpha + bg.blue * bg.alpha * (1 - fg.alpha) / alpha

    return ColorFloat(red, green, blue, alpha)


def combine_colors(fg: Color, bg: Color, opacity: float) -> Color:
    """Like combin() but work with Color objects. Only the fg color has opacity"""
    return combine(
        ColorFloat.from_color(fg, opacity), ColorFloat.from_color(bg)
    ).to_color()
