"""random color filter"""

import random
from configparser import ConfigParser
from importlib.metadata import entry_points

from larry import LOGGER, ColorList

from . import load_filter


def cfilter(
    orig_colors: ColorList, config: ConfigParser
) -> ColorList:  # pragma: no cover
    """Yeah, coz how could we live without a random filter?"""
    filter_names = available_filters(config)

    if not filter_names:
        return orig_colors

    chains = config.getint("filters:random", "chains", fallback=1)

    new_colors = orig_colors
    iters = random.randint(1, chains)

    for _ in range(iters):
        filter_name = random.choice(filter_names)
        filter_ = load_filter(filter_name)
        LOGGER.debug("random: running filter: %s", filter_name)
        new_colors = filter_(new_colors, config)

    return new_colors


def available_filters(config: ConfigParser) -> list[str]:
    """Return a list of available filters config the configuation"""
    all_filters = {i.name for i in entry_points().select(group="larry.filters")}
    include_str = config.get("filters:random", "include", fallback="")
    include_str = include_str.strip()
    add: set[str] = set()
    sub: set[str] = {"random"}

    for i in include_str.split():
        if i.startswith("-"):
            sub.add(i[1:])
        else:
            add.add(i)

    if not add:
        add = set(all_filters)

    available = [i for i in add if i not in sub]
    available.sort()

    return available
