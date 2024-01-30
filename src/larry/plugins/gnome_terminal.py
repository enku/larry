"""Larry plugin for the Gnome Terminal"""

from larry import Color, ColorList
from larry.config import ConfigType

# schema how to set gnome-terminal profiles
SCHEMA = "org.gnome.Terminal.Legacy.Profile"
PATH = "/org/gnome/terminal/legacy/profiles:/:{profile}/"


def plugin(colors: ColorList, config: ConfigType) -> None:
    """larry plugin to set the gnome-terminal background color"""
    Gio = gio()  # pylint: disable=invalid-name

    profiles = config.get("profiles", "").split()
    colorstr = config["color"]
    color = Color(colorstr)

    for profile in profiles:
        path = get_path(profile)
        new_color = color.colorify(colors[0])
        value = str(new_color)
        settings = Gio.Settings.new_with_path(SCHEMA, path)
        settings.set_string("background-color", value)


def get_path(profile: str) -> str:
    """Return the terminal gsettings path for *profile*"""
    return PATH.format(profile=profile)


def gio():  # pragma: no cover
    """Return the Gio gobject introspection object"""
    # Move import here so --list-plugins will at least work w/o gi
    # pylint: disable=import-outside-toplevel,import-error
    from gi.repository import Gio

    return Gio
