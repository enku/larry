"""
Cool color class and functions

Some of this stuff I guessed at and therefore is probably entirely wrong.
I am not a color expert, but here are some resources:

http://www.cs.rit.edu/~ncs/color/t_convert.html


"""
__version__ = (0, 9, 12)

import os
import random
import re

randint = random.randint

gtk = False
if os.environ.get('DISPLAY', None):
    try:
        import gi
        gi.require_version('Gtk', '3.0')

        from gi.repository import Gtk as gtk
    except (ImportError, RuntimeError):
        pass

RGB = '/usr/share/X11/rgb.txt'
_COMPS = ('>', '<', '=')
PASTEL_SATURATION = 50
PASTEL_BRIGHTNESS = 100


class BadColorSpecError(Exception):
    pass


def load_rgb():
    rgb = {}
    for line in open(RGB, 'r').readlines():
        line = line.strip()
        if line[0] == '!' or not line:
            continue
        fields = line.split(None, 3)
        try:
            color = tuple([int(i) for i in fields[:3]])
            color_name = fields[3]
            rgb[color_name.lower()] = color
            #print color_name,'=',color
        except ValueError:
            continue
    return rgb


class Color(object):
    """tuple-like color class"""

    rgb = load_rgb()

    def __init__(self, colorspec=None):
        #object.__init__(self)
        colorspec = colorspec or 'random'
        colorspec_type = type(colorspec)

        if isinstance(colorspec, Color):
            # copy color
            self.red, self.green, self.blue = (colorspec.red, colorspec.green,
                                               colorspec.blue)
            return

        string_type = isinstance(colorspec, str)
        if string_type:
            colorspec = colorspec.strip('"')

        ####(r, g , b)
        if colorspec_type is tuple or colorspec_type is list:
            self.red, self.green, self.blue = [int(i) for i in colorspec]
            return

        ####r/g/b
        elif string_type and len(colorspec.split('/')) == 3:
            self.red, self.green, self.blue = colorspec.split('/')
        ####{ r, g, b}
        elif string_type and colorspec[0] == '{' and colorspec[-1] == '}':
            red, green, blue = colorspec[1:-1].split(',')
            self.red = int(float(red) * 255)
            self.green = int(float(green) * 255)
            self.blue = int(float(blue) * 255)

        elif string_type and colorspec.lower() in self.rgb:
            self.red, self.green, self.blue = self.rgb[colorspec.lower()]

        ####random
        elif colorspec == 'random':
            somecolor = self.randcolor()
            self.red = somecolor.red
            self.blue = somecolor.blue
            self.green = somecolor.green

        elif colorspec[:7] == 'random(':
            l = colorspec[7:-1]
            comp = ''
            value = ''
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
                value = int(value)
            except ValueError:
                raise BadColorSpecError(colorspec)

            somecolor = self.randcolor(value)

            self.red = somecolor.red
            self.blue = somecolor.blue
            self.green = somecolor.green

        ####randhue
        elif colorspec[:8] == 'randhue(':
            parms = colorspec[8:-1].split(',', 1)
            saturation, brightness = float(parms[0]), float(parms[1])
            somecolor = self.randhue(saturation, brightness)
            self.red, self.blue, self.green = (somecolor.red, somecolor.blue,
                                               somecolor.green)

        elif colorspec == 'query' and gtk:
            self.query_color()
            return

        ####rrggbb
        elif string_type and len(colorspec) in [6, 7]:
            triplet = colorspec
            if triplet[0] == '#':
                triplet = triplet[1:]
            self.red = int('%s' % triplet[0:2], 16)
            self.green = int('%s' % triplet[2:4], 16)
            self.blue = int('%s' % triplet[4:6], 16)

        ####rgb
        elif string_type and re.match(r'#[0-9,[A-F]{3}$', colorspec, re.I):
            self.red = int(colorspec[1], 16) * 17
            self.green = int(colorspec[2], 16) * 17
            self.blue = int(colorspec[3], 16) * 17
        else:
            raise BadColorSpecError

    def __repr__(self):
        return '#%02x%02x%02x' % (self.red, self.green, self.blue)

    def __add__(self, value):
        if type(value) is int or type(value) is float:
            red = self.red + value
            blue = self.blue + value
            green = self.green + value

            red, green, blue = [self._sanitize(component)
                                for component in (red, green, blue)]

            return Color((red, green, blue))

    def __mul__(self, value):
        """This should be used instead of __add__ as it makes more sense"""

        if type(value) is int or type(value) is float:
            red = int(self.red * value)
            green = int(self.green * value)
            blue = int(self.blue * value)

            red, green, blue = [self._sanitize(component)
                                for component in (red, green, blue)]

            return Color((red, green, blue))

        elif type(value) is Color:
            clum = value.luminocity()
            return self * clum

    __rmul__ = __mul__

    def __div__(self, value):
        """Just like __mul__"""

        if type(value) is int or type(value) is float:
            return self * (1.0 / value)

        elif type(value) is Color:
            clum = value.luminocity()
            return self / clum

    def __sub__(self, value):
        return self.__add__(-value)

    ####private
    def _sanitize(self, number):
        """Make sure 0 <= number <= 255"""
        number = min(255, number)
        number = max(0, number)

        return number

    ####public
    def colorify(self, color, fix_bw=True):
        """Return new color with color's hue and self's saturation and value"""
        # black and white don't make good HSV values, so we make them
        # imperfect
        if fix_bw and self == Color('white'):
            my_color = Color((254, 254, 254))
        elif fix_bw and self == Color('black'):
            my_color = Color((1, 1, 1))
        else:
            my_color = Color(self)

        my_hsv = my_color.toHSV()
        color_hsv = color.toHSV()

        new_color = Color.fromHSV((color_hsv[0], my_hsv[1], my_hsv[2]))
        return new_color

    @classmethod
    def randcolor(cls, l=None, comp='='):
        """Return random color color.luminocity() = l """

        low_range = 0
        high_range = 255

        color = cls((randint(low_range, high_range), randint(low_range,
                                                             high_range), randint(low_range, high_range)))

        if not l:
            return color

        if comp == '=':
            while True:
                if color.luminocity() == l:
                    return color
                color = cls([randint(low_range, high_range)
                             for i in range(3)])

        if comp == '>':
            while True:
                if color.luminocity() > l:
                    return color
                color = cls([randint(low_range, high_range)
                             for i in range(3)])

        if comp == '<':
            while True:
                if color.luminocity() < l:
                    return color
                color = cls([randint(low_range, high_range)
                             for i in range(3)])

        if comp == '>=':
            while True:
                if color.luminocity() >= l:
                    return color
                color = cls([randint(low_range, high_range)
                             for i in range(3)])

        if comp == '<=':
            while True:
                if color.luminocity() <= l:
                    return color
                color = cls([randint(low_range, high_range)
                             for i in range(3)])

        raise BadColorSpecError('random(%s%s)' % (comp, l))

    def inverse(self):
        """Return inverse of color"""

        return Color((255 - self.red, 255 - self.green, 255 - self.blue))

    def winverse(self):
        """Keep red part, change green to 255-, change blue to 0"""

        return Color((self.red / 2, 255 - self.green, 0))

    def to_gtk(self):
        """return string of Color in gtkrc format"""
        return '{ %.2f, %.2f, %.2f }' % (self.red / 255.0, self.green /
                                         255.0, self.blue / 255.0)

    def luminocity(self):
        """Return (int) luminocity of color"""
        # from http://tinyurl.com/8cve8
        return int(round(0.30 * self.red + 0.59 * self.green + 0.11 * self.blue))

    def pastelize(self):
        """Return a "pastel" version of self"""
        hsv = self.toHSV()
        newcolor = self.fromHSV((hsv[0], PASTEL_SATURATION,
                                 PASTEL_BRIGHTNESS))
        return newcolor

    @classmethod
    def gradient(cls, from_color, to_color, steps):
        """Generator for creating gradients"""
        #print "gradient: from %s to %s" % (from_color, to_color)
        fsteps = float(steps - 1)
        inc_red = (to_color.red - from_color.red) / fsteps
        inc_green = (to_color.green - from_color.green) / fsteps
        inc_blue = (to_color.blue - from_color.blue) / fsteps

        new_red = from_color.red
        new_blue = from_color.blue
        new_green = from_color.green
        #print from_color
        yield from_color
        for step in range(steps - 2):  # minus the 2 endpoints
            step  # unused
            new_red = new_red + inc_red
            new_green = new_green + inc_green
            new_blue = new_blue + inc_blue
            new_color = cls((int(new_red), int(new_green), int(new_blue)))
            #print new_color
            yield new_color
        #print to_color
        yield to_color

    if gtk:
        @classmethod
        def query_color(self):
            """Present a color dialog using GTK widgets. Allows user to select
            colors. sets color selected
            """
            def destroy(widget, event=None):
                widget  # unused
                event  # unused
                my_dialog.hide()
                gtk.main_quit()
                True

            my_dialog = gtk.ColorSelectionDialog("Select a color")
            ok_button = my_dialog.get_property('ok-button')
            ok_button.connect('clicked', destroy)
            cancel_button = my_dialog.get_property('cancel-button')
            cancel_button.connect('clicked', destroy)
            my_dialog.connect('delete_event', destroy)
            my_dialog.show_all()
            gtk.main()
            gdk_color = my_dialog.get_property(
                'color-selection').get_current_color()
            red = gdk_color.red / 257
            green = gdk_color.green / 257
            blue = gdk_color.blue / 257
            my_dialog.destroy()
            self.red = red
            self.green = green
            self.blue = blue

    def factor_tuple(self, mytuple):
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

    def factor(self, myint):
        """Same as factor_tuple, but just one number"""

        return self.factor_tuple((myint, myint, myint))

    @classmethod
    def randhue(cls, saturation, brightness):
        """Create color with random hue based on saturation and brightness"""
        saturation = float(saturation)
        brightness = float(brightness)
        hue = randint(0, 360)
        return Color.fromHSV((hue, saturation, brightness))

    def toHSV(self):
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
            h = -1
        else:
            if r == maximum:
                h = (g - b) / delta
            elif (g == maximum):
                h = 2 + (b - r) / delta
            elif (b == maximum):
                h = 4 + (r - g) / delta
            h = h * 60.0
            if (h < 0):
                h = h + 360.0
        return (h, s * 100.0, v * 100.0)

    @classmethod
    def fromHSV(cls, HSV):
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

if gtk:
    class ColorSelectionGui(gtk.Window):
        """ColorSel class"""

        def __init__(self):

            gtk.Window.__init__(self, type=gtk.WINDOW_TOPLEVEL)
            super(ColorSelectionGui, self).set_title('Select Plugin Color')
            #self.set_title("Select Plugin Color")
            self.set_border_width(5)

            self.vbox = gtk.VBox(spacing=5)

            self.colorbutton = gtk.ColorButton()
            self.specific_hbox = gtk.HBox(spacing=20)
            self.specific_color_radio = gtk.RadioButton(
                label="_Specific Color")

            self.random_hbox = gtk.HBox(spacing=5)
            self.random_color_radio = gtk.RadioButton(
                group=self.specific_color_radio, label="_Random")

            self.random_brightness_radio = gtk.RadioButton(
                group=self.specific_color_radio, label='_With brightness:')

            adjustment = gtk.Adjustment(value=178, lower=0, upper=255,
                                        step_incr=1)
            self.random_spinbutton = gtk.SpinButton(adjustment=adjustment,
                                                    digits=0)

            self.cancel_button = gtk.Button(stock=gtk.STOCK_CANCEL)
            self.set_button = gtk.Button(stock=gtk.STOCK_OK, label='Set')
            self.buttonbox = gtk.HButtonBox()
            self.buttonbox.set_spacing(10)
            self.buttonbox.set_layout(gtk.BUTTONBOX_END)
            self.buttonbox.add(self.cancel_button)
            self.buttonbox.add(self.set_button)

            # put the widgets together
            self.specific_hbox.add(self.specific_color_radio)
            self.specific_hbox.add(self.colorbutton)
            self.random_hbox.add(self.random_color_radio)
            self.random_hbox.add(self.random_brightness_radio)
            self.random_hbox.add(self.random_spinbutton)
            self.vbox.add(self.specific_hbox)
            self.vbox.add(self.random_hbox)
            self.vbox.add(gtk.HSeparator())
            self.vbox.add(self.buttonbox)

            self.add(self.vbox)


class ColorFromGui(object):
    def __init__(self, gui, default_color):
        if default_color is not None:
            self.color = Color(default_color)
        else:
            self.color = None

        self.gui = gui

        # setup callbacks for gui
        self.gui.cancel_button.connect('clicked', self.window_close)
        self.gui.connect('delete_event', self.window_close)
        self.gui.set_button.connect('clicked', self.set_color)

    def window_close(self, *vargs):
        self.gui.hide()
        del self.gui

    def set_color(self, *vargs):
        color = self.gui.colorbutton.get_color()
        red = color.red / 257
        green = color.green / 257
        blue = color.blue / 257
        self.color = Color((red, green, blue))
        self.window_close()


def main(argv):
    """Main program entry point"""
    default_color = 'pink'
    gui = ColorSelectionGui()
    colorc = ColorFromGui(gui, default_color)
    gui.show_all()
    gtk.main()
    color = colorc.color
    print(color)
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
