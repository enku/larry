"""Utils dealing with the larry configuration (file)"""
import configparser
import importlib.resources
import os.path

import platformdirs

DEFAULT_CONFIG_PATH = os.path.join(platformdirs.user_config_dir(), "larry.cfg")
DEFAULT_INPUT_PATH = str(
    importlib.resources.files("larry").joinpath("data/gentoo-cow-gdm-remake.svg")
)

ConfigType = configparser.SectionProxy


def load(path: str) -> configparser.ConfigParser:
    """Return ConfigParser instance given the path"""
    config = configparser.ConfigParser()
    config["DEFAULT"]["input"] = DEFAULT_INPUT_PATH
    config.read(path)

    return config


def get_plugin_config(plugin_name: str, config_path: str) -> ConfigType:
    """Return the config for the given plugin"""
    config = load(config_path)
    plugin_config_name = f"plugins:{plugin_name}"

    if plugin_config_name in config:
        plugin_config = config[plugin_config_name]
    else:
        plugin_config = config[plugin_config_name] = config["DEFAULT"]

    return plugin_config
