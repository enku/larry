"""Replace colors on the Larry the Cow wallpaper"""

from __future__ import annotations

import logging
from importlib.metadata import distribution
from io import BytesIO
from typing import Any, Iterable, Protocol, Type
from warnings import warn

from PIL import Image as PillowImage

from larry.color import COLORS_RE, Color, ColorList, replace_string

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
