"""Plugin for the cal(1) command"""

import platformdirs

from larry import Color, ColorList, ConfigType, io

NAMES = ["today", "weeknumber", "header", "workday", "weekend"]


def plugin(colors: ColorList, _config: ConfigType) -> None:
    """cal colors plugin"""
    colors = [color.pastelize() for color in Color.generate_from(colors, len(NAMES))]
    config = ""

    for color, name in zip(colors, NAMES):
        config = f"{config}{name} 38;2;{color.red};{color.green};{color.blue}\n"

    io.write_file(
        f"{platformdirs.user_config_dir()}/terminal-colors.d/cal.scheme",
        config.encode("UTF-8"),
    )
