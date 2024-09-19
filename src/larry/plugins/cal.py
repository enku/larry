"""Plugin for the cal(1) command"""

import platformdirs

from larry import Color, ColorList, io
from larry.config import ConfigType

NAMES = ["today", "weeknumber", "header", "workday", "weekend"]
NORMAL = 2
BOLD = 1


def plugin(colors: ColorList, _config: ConfigType) -> None:
    """cal colors plugin"""
    colors = [color.pastelize() for color in Color.generate_from(colors, len(NAMES))]
    config = ""

    for color, name in zip(colors, NAMES):
        weight = BOLD if name == "today" else NORMAL
        config = f"{config}{name} 38;{weight};{color.red};{color.green};{color.blue}\n"

    io.write_text_file(
        f"{platformdirs.user_config_dir()}/terminal-colors.d/cal.scheme", config
    )
