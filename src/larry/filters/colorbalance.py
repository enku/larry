"""colorbalance color filter"""

from configparser import ConfigParser

from larry.color import Color, ColorList


def cfilter(orig_colors: ColorList, _config: ConfigParser) -> ColorList:
    """Adjust the colors to achieve a more harmonious color scheme"""
    new_colors: ColorList = []
    size = len(orig_colors)
    normalized = [(c.red / 255, c.green / 255, c.blue / 255) for c in orig_colors]
    average = [sum(c[i] for c in normalized) / size for i in range(3)]

    for c in normalized:
        adjusted = [min(max(c[i] + (average[i] - c[i]) * 0.5, 0), 1) for i in range(3)]
        new_colors.append(
            Color(
                int(adjusted[0] * 255), int(adjusted[1] * 255), int(adjusted[2] * 255)
            )
        )

    return new_colors
