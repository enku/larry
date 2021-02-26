"""Larry plugin to run a shell command"""
import subprocess
from typing import List

from larry import LOGGER, ConfigType
from larry.types import Color


def plugin(colors: List[Color], config: ConfigType) -> None:
    """run a command with the colors as stdin"""
    LOGGER.debug("command plugin begin")
    exe = config["command"]
    colors_str = "\n".join(str(i) for i in colors)

    LOGGER.debug('command="%s"', exe)
    subprocess.run([exe], check=False, input=colors_str.encode())
