"""Larry plugin to run a shell command"""
import subprocess

from larry import LOGGER, ColorList
from larry.config import ConfigType


def plugin(colors: ColorList, config: ConfigType) -> None:
    """run a command with the colors as stdin"""
    LOGGER.debug("command plugin begin")
    exe = config["command"]
    colors_str = "\n".join(str(i) for i in colors)

    LOGGER.debug('command="%s"', exe)
    subprocess.run(exe, check=False, shell=True, input=colors_str.encode())
