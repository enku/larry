"""type definitions for filters"""

from configparser import ConfigParser
from typing import Callable

from larry import ColorList

Filter = Callable[[ColorList, ConfigParser], ColorList]


class FilterNotFound(LookupError):
    """Unable to find the requested filter"""


class FilterError(RuntimeError):
    """Filter cannot run successfully"""
