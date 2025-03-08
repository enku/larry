"""Replace colors on the Larry the Cow wallpaper"""

import logging
from importlib.metadata import distribution

from larry.color import Color, ColorList

__all__ = ("__version__", "LOGGER", "Color", "ColorList")
__version__ = distribution("larry").version

LOGGER = logging.getLogger("larry")
