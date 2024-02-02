"""Misc utility functions"""

import random


def between(value, min_value, max_value) -> bool:
    """Return true if value is between 0 and 1 (inclusive)"""
    return min_value <= value <= max_value


def clip(value, *, minimum=0, maximum=255):
    """Return value that is no larger than maximum and no smaller than minimum"""
    value = min(value, maximum)
    value = max(value, minimum)

    return value


def parse_range(string: str) -> tuple[int, int] | tuple[float, float]:
    """Given a string like "min max" return the range (min, max)

    Ensure that (min, max) are either both floats or both ints.
    Raise ValueError if min > max
    """
    parts = string.strip().split(None, 1)

    if len(parts) != 2:
        raise ValueError("String must be a whitespace-separated range of 2 numbers")

    lower = float(parts[0])
    upper = float(parts[1])

    if lower > upper:
        raise ValueError("Lower value must not be greater than upper value")

    if lower.is_integer() and upper.is_integer():
        return int(lower), int(upper)

    return lower, upper


def randsign(num: int) -> int:
    """Return a random integer between -num and num"""
    return random.choice([-1, 1]) * random.randint(0, num)
