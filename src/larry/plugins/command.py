"""Larry plugin to run a shell command"""

import subprocess
from functools import partial

from larry import LOGGER, ColorList
from larry.config import ConfigType
from larry.pool import run

from . import apply_plugin_filter


async def plugin(colors: ColorList, config: ConfigType) -> None:
    """run a command with the colors as stdin"""
    LOGGER.debug("command plugin begin")
    colors = apply_plugin_filter(colors, config)
    exe = config.get("command", fallback="")

    if not exe:
        return

    colors_str = "\n".join(str(i) for i in colors)

    LOGGER.debug('command="%s"', exe)
    func = partial(subprocess.run, check=False, shell=True, input=colors_str.encode())
    await run(func, exe)
