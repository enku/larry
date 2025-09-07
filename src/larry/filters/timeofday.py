"""time of day color filter"""

import datetime as dt
import sys
from configparser import ConfigParser
from enum import IntEnum, unique

from larry.color import Color, ColorList


@unique
class TimeOfDay(IntEnum):
    """Different times of day (and what hour they start)"""

    MORNING = 6
    MIDDAY = 12
    EVENING = 18
    NIGHT = 21


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
    time_of_day = get_time_of_day(time)
    next_time_of_day = get_next_time_of_day(time_of_day)
    percentage = (time.hour - min(time_of_day, next_time_of_day)) / abs(
        time_of_day - next_time_of_day
    )
    factors = get_factors(config)
    factor_range = factors[time_of_day]
    diff = factor_range[1] - factor_range[0]

    return percentage * diff + factor_range[0]


def get_time_of_day(time: dt.datetime) -> TimeOfDay:
    """Given the time return what TimeOfDay it is"""
    hour = time.hour

    if TimeOfDay.MORNING <= hour < TimeOfDay.MIDDAY:
        return TimeOfDay.MORNING
    if TimeOfDay.MIDDAY <= hour < TimeOfDay.EVENING:
        return TimeOfDay.MIDDAY
    if TimeOfDay.EVENING <= hour < TimeOfDay.NIGHT:
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
