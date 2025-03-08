"""Replace colors on the Larry the Cow wallpaper"""

import logging
from importlib.metadata import distribution
from typing import Any
from warnings import warn

from larry.color import Color, ColorList

__all__ = ("__version__", "LOGGER", "Color", "ColorList")
__version__ = distribution("larry").version

LOGGER = logging.getLogger("larry")


def __getattr__(name: str) -> Any:
    if name == "ConfigType":
        warn(
            "larry.ConfigType is deprecated. Use larry.config.ConfigType",
            DeprecationWarning,
            stacklevel=2,
        )
        import larry.config  # pylint: disable=import-outside-toplevel

        return larry.config.ConfigType

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
