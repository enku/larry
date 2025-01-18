"""Larry color filters

Filters are functions that take a list of colors and return a list of colors, possibly
doing "something" to them.
"""

import io
import typing as t
from configparser import ConfigParser
from importlib.metadata import entry_points

from larry.color import ColorGenerator
from larry.config import load as load_config

Filter = t.Callable[[ColorGenerator, int, ConfigParser], ColorGenerator]


class FilterNotFound(LookupError):
    """Unable to find the requested filter"""


class FilterError(RuntimeError):
    """Filter cannot run successfully"""


def list_filters(config_path: str) -> str:
    """Return text displaying available filters and enabled status"""
    output = io.StringIO()
    config = load_config(config_path)
    enabled_filter = config["larry"].get("filter", "gradient").split()

    for name, func in filters_list():
        func_doc = func.__doc__ or ""
        doc = func_doc.split("\n", 1)[0].strip()
        enabled = "X" if name in enabled_filter else " "

        print(f"[{enabled}] {name:20} {doc}", file=output)

    return output.getvalue()


def load_filter(name: str) -> Filter:
    """Load the filter with the given name"""
    filters = entry_points().select(group="larry.filters", name=name)

    if not filters:
        raise FilterNotFound(name)

    try:
        return tuple(filters)[0].load()
    except ModuleNotFoundError as error:
        raise FilterNotFound(name) from error


def filters_list() -> list[tuple[str, Filter]]:
    """Return a list of tuple of (filter_name, filter_func) for all filters"""
    return [(i.name, i.load()) for i in entry_points().select(group="larry.filters")]
