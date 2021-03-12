"""Plugin to set the background colors in GNOME"""
from gi.repository import Gio

from larry import ConfigType
from larry.types import ColorList

SCHEMA = "org.gnome.desktop.background"


def plugin(colors: ColorList, _config: ConfigType) -> None:
    """GNOME background color plugin"""
    primary_color = colors[0]
    secondary_color = colors[-1]
    settings = Gio.Settings.new(SCHEMA)

    settings.set_string("primary-color", str(primary_color))
    settings.set_string("secondary-color", str(secondary_color))
    settings.apply()
