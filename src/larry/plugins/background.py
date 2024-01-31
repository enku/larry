"""Plugin to set the background colors in GNOME"""

from larry import ColorList
from larry.config import ConfigType
from larry.plugins import gir

SCHEMA = "org.gnome.desktop.background"


def plugin(colors: ColorList, _config: ConfigType) -> None:
    """GNOME background color plugin"""
    gi_repo = gir()

    primary_color = colors[0]
    secondary_color = colors[-1]
    settings = gi_repo.Gio.Settings.new(SCHEMA)

    settings.set_string("primary-color", str(primary_color))
    settings.set_string("secondary-color", str(secondary_color))
    settings.apply()
