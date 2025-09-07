"""sepia color filter"""

from configparser import ConfigParser
from dataclasses import dataclass
from functools import partial

from larry.color import Color, ColorList
from larry.utils import clip


@dataclass
class Channel:
    """Coefficients for a given RGB channel"""

    base: float
    multiplier: float
    adjustment: float


CHANNELS = {
    "red": Channel(base=0.393, multiplier=0.607, adjustment=0.272),
    "green": Channel(base=0.769, multiplier=0.314, adjustment=0.534),
    "blue": Channel(base=0.189, multiplier=0.168, adjustment=0.131),
}


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Apply a sepia effect to the given colors"""
    rc = Channel(
        get(config, "red_base"),
        get(config, "red_multiplier"),
        get(config, "red_adjustment"),
    )
    gc = Channel(
        get(config, "green_base"),
        get(config, "green_multiplier"),
        get(config, "green_adjustment"),
    )
    bc = Channel(
        get(config, "blue_base"),
        get(config, "blue_multiplier"),
        get(config, "blue_adjustment"),
    )
    amount = config.getfloat("filters:sepia", "amount", fallback=1.0)

    return [blend(c, sepia(c, rc, gc, bc), amount) for c in orig_colors]


def sepia(color: Color, rc: Channel, gc: Channel, bc: Channel) -> Color:
    """Return the sepia color of the given color

    Given the channel coefficients
    """
    ic = partial(lambda x: int(clip(x)))  # sneaking around pylint

    return Color(
        ic(rc.base * color.red + rc.multiplier * color.green + bc.base * color.blue),
        ic(
            rc.adjustment * color.red
            + gc.base * color.green
            + bc.multiplier * color.blue
        ),
        ic(
            bc.adjustment * color.red
            + gc.multiplier * color.green
            + bc.base * color.blue
        ),
    )


def blend(orig_color: Color, sepia_color: Color, amount: float) -> Color:
    """Blend the original color with the sepia color by the given amount

    amount is between 0 and 1 where 1 is 100% sepia and 0 is 100% original.
    """
    if amount == 1:
        return sepia_color

    if amount == 0:
        return orig_color

    return Color(
        clip((1 - amount) * orig_color.red + amount * sepia_color.red),
        clip((1 - amount) * orig_color.green + amount * sepia_color.green),
        clip((1 - amount) * orig_color.blue + amount * sepia_color.blue),
    )


def get(config: ConfigParser, name: str) -> float:
    """Return the channel coefficient given the name

    Returns the value in config or the default.
    """
    channel, _, attr = name.partition("_")
    default = getattr(CHANNELS[channel], attr)

    return config.getfloat("filters:sepia", name, fallback=default)
