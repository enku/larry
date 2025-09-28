"""Larry plugins"""

import importlib
import io
from configparser import ConfigParser
from functools import cache, wraps
from importlib.metadata import entry_points
from inspect import iscoroutinefunction
from typing import Any, Callable, List, Tuple, TypeAlias

from larry import LOGGER, config
from larry.color import ColorList
from larry.config import ConfigType
from larry.filters import load_filter
from larry.pool import run

PluginType: TypeAlias = Callable[[ColorList, config.ConfigType], Any]
PLUGINS: dict[str, PluginType] = {}


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


async def do_plugin(plugin_name: str, colors: ColorList, config_path: str) -> None:
    """Run the given plugin"""
    try:
        plugin = await run(load, plugin_name)
    except PluginNotFound:
        LOGGER.warning("plugin %s not found", plugin_name)
        return

    plugin_config = config.get_plugin_config(plugin_name, config_path)

    LOGGER.debug("Running plugin for %s", plugin_name)

    if iscoroutinefunction(plugin):
        await plugin(colors, plugin_config)
    else:
        LOGGER.warning("plugin %s not asynchronous", plugin_name)
        plugin(colors, plugin_config)


def plugins_list() -> List[Tuple[str, PluginType]]:
    """Return a list of 2-tuple (pluginname, pluginfunc)"""
    return [(i.name, i.load()) for i in entry_points().select(group="larry.plugins")]


def list_plugins(config_path: str) -> str:
    """List all the beautiful plugins"""
    output = io.StringIO()
    larry_config = config.load(config_path)
    enabled_plugins = larry_config["larry"].get("plugins", "").split()

    for name, func in plugins_list():
        doc = func.__doc__ or ""
        doc = doc.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_plugins else " "
        print(f"[{enabled}] {name:20} {doc}", file=output)

    return output.getvalue()


@cache
def load(name: str) -> PluginType:
    """Load and return the given plugin"""
    if name not in PLUGINS:
        plugins = [
            i for i in entry_points().select(group="larry.plugins") if i.name == name
        ]

        if not plugins:
            raise PluginNotFound(name)

        try:
            plugin = plugins[0].load()
        except ModuleNotFoundError as error:  # pragma: no cover
            raise PluginNotFound(name) from error

        PLUGINS[name] = plugin

    return PLUGINS[name]


class GIRepository:  # pylint: disable=too-few-public-methods
    """Proxy for the gobject introspection repository

    Used so that the plugins don't have to import gi.repository at the top-level
    --list-plugins will at least work w/o gi.
    """

    Gio: Any

    def __getattr__(self, name: str):  # pragma: no cover
        repo = importlib.__import__("gi.repository", fromlist=[name])

        return getattr(repo, name)


gir = GIRepository()


def apply_plugin_filter(colors: ColorList, plugin_config: ConfigType) -> ColorList:
    """Apply the colors to the effect(s) given in the config

    Some plugins can apply filters. The config is similar to the "global" filter for the
    image. For example the "command" plugin, which can apply filters, can be configured
    accordingly:

    [plugins:command]
    filter = inverse neonize
    filter.neonize.brightness = 50
    """
    colors = list(colors)

    if not (filter_names := plugin_config.get("filter", "").split()):
        return colors

    for name in filter_names:
        cfilter = load_filter(name)
        global_config = global_config_for_filter(name, plugin_config)
        colors = cfilter(colors, global_config)

    return colors


def global_config_for_filter(name, plugin_config: ConfigType) -> ConfigParser:
    """Create a ConfigParser given the plugin config and filter name"""
    section = f"filters:{name}"
    prefix = f"filter.{name}."
    parser = ConfigParser()

    parser.add_section(section)

    for key, value in plugin_config.items():
        if key.startswith(prefix):
            parser.set(section, key.removeprefix(prefix), value)

    return parser
