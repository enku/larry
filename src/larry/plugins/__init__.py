"""Larry plugins"""
from typing import Callable, Dict, List

import pkg_resources

from larry import LOGGER, Color, ColorList, ConfigType, load_config

PluginType = Callable[[ColorList, ConfigType], None]
PLUGINS: Dict[str, PluginType] = {}


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
        plugin_config = config[plugin_config_name] = {}

    return plugin_config


def plugins_list():
    return [
        (i.name, i.load()) for i in pkg_resources.iter_entry_points("larry.plugins")
    ]


def load(name: str):
    if name not in PLUGINS:
        iter_ = pkg_resources.iter_entry_points("larry.plugins", name)

        try:
            plugin = next(iter_).load()
        except (ModuleNotFoundError, StopIteration) as error:
            raise PluginNotFound(name) from error

        PLUGINS[name] = plugin

    return PLUGINS[name]
