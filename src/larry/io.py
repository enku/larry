"""I/O stuff for larry"""
import os
import subprocess

import aionotify

from larry import LOGGER


def read_file(filename: str) -> bytes:
    pipe_exec = filename.startswith("!")

    if pipe_exec:
        popen = subprocess.Popen(
            os.path.expanduser(filename[1:]), shell=True, stdout=subprocess.PIPE
        )
        content = popen.stdout.read()
    else:
        with open(os.path.expanduser(filename), "rb") as myfile:
            content = myfile.read()

    return content


def write_file(filename: str, data: bytes) -> int:
    """write open *filename* and write *data* to it"""
    head = os.path.split(filename)[0]

    if head:
        os.makedirs(head, exist_ok=True)

    with open(filename, "wb") as myfile:
        return myfile.write(data)


async def watch_file(watcher: aionotify.Watcher, loop, handler):
    try:
        await watcher.setup(loop)
    except OSError as error:
        LOGGER.warning(error)

        return

    while True:
        await watcher.get_event()
        handler()