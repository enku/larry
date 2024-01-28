"""Utils dealing with the larry configuration (file)"""

import configparser
import importlib.resources
import io
import os.path
import tomllib
from typing import Any

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

    try:
        config.read(path)
    except configparser.ParsingError:
        return load_toml_config(path)

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


def load_toml_config(path: str) -> configparser.ConfigParser:
    """Return the TOML config file as a ConfigParser object"""
    with open(path, "rb") as config_fp:
        toml = tomllib.load(config_fp)

    return config_from_toml(toml)


def config_from_toml(toml: dict[str, dict[str, Any]]) -> configparser.ConfigParser:
    """Return the dict as a ConfigParser object"""
    toml = toml.copy()
    config_io = io.StringIO()

    sep = ""

    for title, table in toml.items():
        if not isinstance(table, dict):
            continue
        config_io.write(sep)
        config_io.write(str_from_table(title, table))
        sep = "\n"

    config = configparser.ConfigParser()
    config["DEFAULT"]["input"] = DEFAULT_INPUT_PATH

    config.read_string(config_io.getvalue())

    return config


def str_from_table(name: str, values: dict[str, Any]) -> str:
    """Given the key/value dict and table name, return equivalent INI string"""
    table_io = io.StringIO()
    table_io.write(f"[{name}]\n")

    for key, value in values.items():
        if isinstance(value, dict):
            table_io.write("\n")
            table_io.write(str_from_table(f"{name}.{key}", value))
        else:
            table_io.write(f"{key} = {str_from_config_value(value)}\n")

    return table_io.getvalue()


def str_from_config_value(value: Any) -> str:
    """Return the given Python value as an INI value

    Takes care of converting a list into newline-delimited sting values.
    """
    if isinstance(value, str):
        return value

    if isinstance(value, list):
        return "\n    ".join(str_from_config_value(item) for item in value)

    return repr(value)
