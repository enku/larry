"""time of day color filter"""

import datetime as dt
import sys
from configparser import ConfigParser
from enum import StrEnum, auto, unique
from typing import TypeAlias

from larry.color import Color, ColorList


@unique
class TimeOfDay(StrEnum):
    """Different times of day (and what hour they start)"""

    MORNING = auto()
    MIDDAY = auto()
    EVENING = auto()
    NIGHT = auto()


StartTable: TypeAlias = dict[TimeOfDay, int]

DEFAULT_START: StartTable = {
    TimeOfDay.MORNING: 6,
    TimeOfDay.MIDDAY: 12,
    TimeOfDay.EVENING: 18,
    TimeOfDay.NIGHT: 21,
}
DEFAULT_FACTORS = {
    TimeOfDay.MORNING: (0.8, 1.0),
    TimeOfDay.MIDDAY: (1.0, 1.0),
    TimeOfDay.EVENING: (1.0, 0.6),
    TimeOfDay.NIGHT: (0.5, 0.5),
}

now = dt.datetime.now


def cfilter(orig_colors: ColorList, config: ConfigParser) -> ColorList:
    """Adjust brightness according to the time of day"""
    time = now()
    factor = get_brightness_factor(time, config)

    # return [next(palette).colorify(color) for color in orig_colors]
    return [
        Color.from_hsv((h, s, factor * v))
        for color in orig_colors
        for h, s, v in [color.to_hsv()]
    ]


def get_brightness_factor(time: dt.datetime, config: ConfigParser) -> float:
    """Given the time return the factor of the brightness to be used"""
    starts = get_start_table(config)
    time_of_day = get_time_of_day(time, starts)
    next_time_of_day = get_next_time_of_day(time_of_day)
    time_of_day_hour = starts[time_of_day]
    next_time_of_day_hour = starts[next_time_of_day]
    percentage = (time.hour - min(time_of_day_hour, next_time_of_day_hour)) / abs(
        time_of_day_hour - next_time_of_day_hour
    )
    factors = get_factors(config)
    factor_range = factors[time_of_day]
    diff = factor_range[1] - factor_range[0]

    return percentage * diff + factor_range[0]


def get_time_of_day(time: dt.datetime, starts: StartTable) -> TimeOfDay:
    """Given the time return what TimeOfDay it is"""
    hour = time.hour

    if starts[TimeOfDay.MORNING] <= hour < starts[TimeOfDay.MIDDAY]:
        return TimeOfDay.MORNING
    if starts[TimeOfDay.MIDDAY] <= hour < starts[TimeOfDay.EVENING]:
        return TimeOfDay.MIDDAY
    if starts[TimeOfDay.EVENING] <= hour < starts[TimeOfDay.NIGHT]:
        return TimeOfDay.EVENING
    return TimeOfDay.NIGHT


def get_next_time_of_day(time_of_day: TimeOfDay) -> TimeOfDay:
    """Return the next TimeOfDay of the given TimeOfDay"""
    tod_list = list(TimeOfDay)

    try:
        return tod_list[tod_list.index(time_of_day) + 1]
    except IndexError:
        return tod_list[0]


def get_factors(config: ConfigParser) -> dict[TimeOfDay, tuple[float, float]]:
    """Get the factor range for each TimeOfDay

    If provided in the config, uses values from the config. Otherwise uses the defaults.
    """
    factors = DEFAULT_FACTORS.copy()

    for time_of_day in TimeOfDay:
        option = f"{time_of_day.name.lower()}_factors"

        if value := config.get("filters:timeofday", option, fallback=""):
            if factor_range := parse_range(value):
                factors[time_of_day] = factor_range
            else:
                print(f"Invalid range for {option}: {value!r}", file=sys.stderr)

    return factors


def get_start_table(config) -> StartTable:
    """Return a StartTable based on the config using the default DEFAULT_START"""
    starts = DEFAULT_START.copy()
    start: int | None

    for timeofday in starts:
        option = timeofday.lower()

        if start := config.getint("filters:timeofday", option, fallback=None):
            starts[timeofday] = start

    return starts


def parse_range(range_str: str) -> tuple[float, float] | None:
    """Parse float range from the config string

    range_str should look like:

        "0.8 - 1.0"

    If the string is not parsable, None is returned.
    """
    start, dash, stop = range_str.partition("-")

    if not all([start, dash, stop]):
        return None

    return (float(start.strip()), float(stop.strip()))
