"""Color manipulation utility"""
import operator
import random
import re
from math import floor
from typing import Optional, Tuple, Union

ColorSpecType = Union[str, "Color", Tuple[int, int, int]]
_COMPS = (">", "<", "=")


class BadColorSpecError(ValueError):
    """Exception when an invalid spec was passed to the Color initializer"""


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

        my_hsv = my_color.to_hsv()
        color_hsv = color.to_hsv()

        new_color = Color.from_hsv((color_hsv[0], my_hsv[1], my_hsv[2]))
        return new_color

    @classmethod
    def randcolor(cls, lum: Optional[float] = None, comp: str = "=") -> "Color":
        """Return random color color.luminocity() = lum"""

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

        if not lum:
            return color

        try:
            oper = ops[comp]
        except KeyError:
            raise BadColorSpecError("random(%s%s)" % (comp, lum))

        while True:
            if oper(color.luminocity(), lum):
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
        hsv = self.to_hsv()

        return self.from_hsv((hsv[0], self.PASTEL_SATURATION, self.PASTEL_BRIGHTNESS))

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
    def from_hsv(cls, hsv: Tuple[float, float, float]) -> "Color":
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

    @classmethod
    def load_rgb(cls):
        """Load the rgb.txt name-to-value file"""
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
