"""Larry plugin to run a shell command"""
import subprocess
from typing import List

from larry import LOGGER, Color, ConfigType


def plugin(colors: List[Color], config: ConfigType) -> None:
    """run a command with the colors as arguments"""
    LOGGER.debug('command plugin begin')
    exe = config['command']
    colors_str = [str(i) for i in colors]

    LOGGER.debug('command="%s"', exe)
    subprocess.call([exe] + colors_str)
