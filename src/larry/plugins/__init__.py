"""Larry plugins"""
from importlib.metadata import entry_points
from typing import Callable, List, Tuple

from larry import LOGGER, Color, ColorList, ConfigType, load_config

PluginType = Callable[[ColorList, ConfigType], None]
PLUGINS: dict[str, PluginType] = {}


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


def do_plugin(plugin_name: str, colors: ColorList) -> None:
    plugin = load(plugin_name)
    config = get_config(plugin_name)

    LOGGER.debug("Running plugin for %s", plugin_name)
    plugin(colors, config)


def get_config(plugin_name: str) -> ConfigType:
    config = load_config()
    plugin_config_name = f"plugins:{plugin_name}"

    if plugin_config_name in config:
        plugin_config = config[plugin_config_name]
    else:
        plugin_config = config[plugin_config_name] = config["DEFAULT"]

    return plugin_config


def plugins_list() -> List[Tuple[str, PluginType]]:
    return [(i.name, i.load()) for i in entry_points()["larry.plugins"]]


def load(name: str) -> PluginType:
    if name not in PLUGINS:
        plugins = [i for i in entry_points()["larry.plugins"] if i.name == name]

        if not plugins:
            raise PluginNotFound(name)

        try:
            plugin = plugins[0].load()
        except ModuleNotFoundError as error:
            raise PluginNotFound(name) from error

        PLUGINS[name] = plugin

    return PLUGINS[name]
