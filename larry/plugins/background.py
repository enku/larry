"""Plugin to set the background colors in GNOME"""
from typing import List

from gi.repository import Gio

from larry import Color, ConfigType

SCHEMA = "org.gnome.desktop.background"


def plugin(colors: List[Color], config: ConfigType) -> None:
    """GNOME background color plugin"""
    primary_color = colors[0]
    secondary_color = colors[-1]
    settings = Gio.Settings.new(SCHEMA)

    settings.set_string("primary-color", str(primary_color))
    settings.set_string("secondary-color", str(secondary_color))
    settings.apply()
