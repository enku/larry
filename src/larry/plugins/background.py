"""Plugin to set the background colors in GNOME"""
from larry import ColorList, ConfigType

SCHEMA = "org.gnome.desktop.background"


def plugin(colors: ColorList, _config: ConfigType) -> None:
    """GNOME background color plugin"""
    # Move import here so --list-plugins will at least work w/o gi
    from gi.repository import Gio  # pylint: disable=import-outside-toplevel

    primary_color = colors[0]
    secondary_color = colors[-1]
    settings = Gio.Settings.new(SCHEMA)

    settings.set_string("primary-color", str(primary_color))
    settings.set_string("secondary-color", str(secondary_color))
    settings.apply()
