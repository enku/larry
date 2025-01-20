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
    try:
        include_str = config["filters:random"]["include"]
    except KeyError:
        filter_names = [*{i.name for i in entry_points().select(group="larry.filters")}]
        filter_names.remove("random")
    else:
        filter_names = [*{i.strip() for i in include_str.split()}]

    if not filter_names:
        return orig_colors

    chains = config["filters:random"].getint("chains", fallback=1)

    new_colors = orig_colors
    iters = random.randint(1, chains)

    num_colors = len(orig_colors)
    for _ in range(iters):
        filter_name = random.choice(filter_names)
        filter_ = load_filter(filter_name)
        LOGGER.debug("random: running filter: %s", filter_name)
        new_colors = filter_(new_colors, num_colors, config)

    return new_colors
