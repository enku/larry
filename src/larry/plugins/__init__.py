"""Larry plugins"""

import importlib
import io
from configparser import ConfigParser
from functools import cache, wraps
from importlib.metadata import entry_points
from typing import Any, Callable, List, Tuple, TypeAlias

from larry import LOGGER, config
from larry.color import ColorList
from larry.config import ConfigType
from larry.filters import FilterNotFound, list_filters, load_filter

PluginType: TypeAlias = Callable[[ColorList, config.ConfigType], Any]
PLUGINS: dict[str, PluginType] = {}


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


def do_plugin(plugin_name: str, colors: ColorList, config_path: str) -> None:
    """Run the given plugin"""
    plugin = load(plugin_name)
    plugin_config = config.get_plugin_config(plugin_name, config_path)

    LOGGER.debug("Running plugin for %s", plugin_name)
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


def filtered(plugin: PluginType) -> PluginType:
    """Apply filters to the given plugin"""

    @wraps(plugin)
    def wrapper(colors: ColorList, config_: ConfigType) -> Any:
        for filter_name in (config_.get("filter") or "").split():
            cfilter = load_filter(filter_name)
            colors = cfilter(colors, make_filter_config(filter_name, config_))

        return plugin(colors, config_)

    return wrapper


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


def make_filter_config(filter_name, plugin_config: ConfigType) -> ConfigParser:
    """Create a "filter config" for the given filter given plugin options"""
    config_parser = ConfigParser()
    config_parser.add_section(f"filters:{filter_name}")
    filter_config_prefix = f"filters:{filter_name}:"
    offset = len(filter_config_prefix)

    for key, value in plugin_config.items():
        if key.startswith(filter_config_prefix):
            config_parser[f"filters:{filter_name}"][key[offset:]] = value

    return config_parser
