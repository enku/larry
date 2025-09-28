"""Plugin to set the background colors in GNOME"""

from larry import ColorList
from larry.config import ConfigType
from larry.plugins import apply_plugin_filter, gir
from larry.pool import run

SCHEMA = "org.gnome.desktop.background"


async def plugin(colors: ColorList, config: ConfigType) -> None:
    """GNOME background color plugin"""
    primary_color = colors[0]
    secondary_color = colors[-1]
    primary_color, secondary_color = apply_plugin_filter(
        [primary_color, secondary_color], config
    )
    settings = gir.Gio.Settings.new(SCHEMA)

    await run(settings.set_string, "primary-color", str(primary_color))
    await run(settings.set_string, "secondary-color", str(secondary_color))
    await run(settings.apply)
