"""Larry plugin for the Gnome Terminal"""
from gi.repository import Gio

from larry import Color, ColorList, ConfigType

# schema how to set gnome-terminal profiles
SCHEMA = "org.gnome.Terminal.Legacy.Profile"
PATH = "/org/gnome/terminal/legacy/profiles:/:{profile}/"


def plugin(colors: ColorList, config: ConfigType) -> None:
    """larry plugin to set the gnome-terminal background color"""
    profiles = config.get("profiles", "").split()
    colorstr = config["color"]
    color = Color("#" + colorstr)

    for profile in profiles:
        path = get_path(profile)
        new_color = color.colorify(colors[0])
        value = str(new_color)
        settings = Gio.Settings.new_with_path(SCHEMA, path)
        settings.set_string("background-color", value)


def get_path(profile: str) -> str:
    """Return the terminal gsettings path for *profile*"""
    return PATH.format(profile=profile)
