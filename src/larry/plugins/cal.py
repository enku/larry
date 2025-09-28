"""Plugin for the cal(1) command"""

import platformdirs

from larry import Color, ColorList, io
from larry.config import ConfigType
from larry.plugins import apply_plugin_filter

NAMES = ["today", "weeknumber", "header", "workday", "weekend"]
NORMAL = 2
BOLD = 1


async def plugin(colors: ColorList, config: ConfigType) -> None:
    """cal colors plugin"""
    colors = apply_plugin_filter(list(Color.generate_from(colors, len(NAMES))), config)
    scheme = ""

    for color, name in zip(colors, NAMES):
        weight = BOLD if name == "today" else NORMAL
        scheme = f"{scheme}{name} 38;{weight};{color.red};{color.green};{color.blue}\n"

    io.write_text_file(
        f"{platformdirs.user_config_dir()}/terminal-colors.d/cal.scheme", scheme
    )
