"""Larry color filters

Filters are functions that take a list of colors and return a list of colors, possibly
doing "something" to them.
"""

from larry.filters.types import Filter, FilterError, FilterNotFound
from larry.filters.utils import filters_list, list_filters, load_filter

__all__ = (
    "Filter",
    "FilterError",
    "FilterNotFound",
    "filters_list",
    "list_filters",
    "load_filter",
)
