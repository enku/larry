"""I/O stuff for larry"""
import os
import subprocess


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
