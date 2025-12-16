"""PID larry plugin"""

import os
from pathlib import Path

from larry import io
from larry.color import ColorList
from larry.config import ConfigType
from larry.pool import run


async def plugin(_colors: ColorList, config: ConfigType) -> None:
    """write larry's process id (pid) to a file"""
    output_config = config.get("output", fallback="~/.larry.pid")
    output = Path(output_config).expanduser()

    await run(io.write_file, str(output), bytes(str(os.getpid()), "utf-8"))
