"""Larry plugins"""
import io
from importlib.metadata import entry_points
from typing import Any, Callable, List, Tuple

from larry import LOGGER, Color, ColorList, ConfigType, load_config

PluginType = Callable[[ColorList, ConfigType], Any]
PLUGINS: dict[str, PluginType] = {}


class PluginNotFound(LookupError):
    """Unable to find the requested plugin"""


def do_plugin(plugin_name: str, colors: ColorList, config_path: str) -> None:
    plugin = load(plugin_name)
    config = get_config(plugin_name, config_path)

    LOGGER.debug("Running plugin for %s", plugin_name)
    plugin(colors, config)


def get_config(plugin_name: str, config_path: str) -> ConfigType:
    config = load_config(config_path)
    plugin_config_name = f"plugins:{plugin_name}"

    if plugin_config_name in config:
        plugin_config = config[plugin_config_name]
    else:
        plugin_config = config[plugin_config_name] = config["DEFAULT"]

    return plugin_config


def plugins_list() -> List[Tuple[str, PluginType]]:
    return [(i.name, i.load()) for i in entry_points()["larry.plugins"]]


def list_plugins(config_path: str) -> str:
    """List all the beautiful plugins"""
    output = io.StringIO()
    config = load_config(config_path)
    enabled_plugins = config["larry"].get("plugins", "").split()

    for name, func in plugins_list():
        doc = func.__doc__ or ""
        doc = doc.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_plugins else " "
        print(f"[{enabled}] {name:20} {doc}", file=output)

    return output.getvalue()


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
