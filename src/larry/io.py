"""I/O stuff for larry"""
import os
import subprocess as sp


def read_file(filename: str) -> bytes:
    """open filename and read data from it

    If filename starts with "!" then treat the rest as a shell command, run it in a
    shell and return it's standout output
    """
    pipe_exec = filename.startswith("!")

    if pipe_exec:
        command = filename[1:]
        with sp.Popen(command, shell=True, stdout=sp.PIPE) as popen:
            assert popen.stdout
            return popen.stdout.read()

    filename = os.path.expanduser(filename)
    with open(filename, "rb") as myfile:
        return myfile.read()


def write_file(filename: str, data: bytes) -> int:
    """open filename and write data to it

    If filename starts with "!" then treat the rest as a shell command, run it in a
    shell and write data to it's standard input

    Returns bytes written if it is a regular filename else returns the status code of
    the shell command.
    """
    pipe_exec = filename.startswith("!")

    if pipe_exec:
        command = filename[1:]
        with sp.Popen(command, shell=True, stdin=sp.PIPE) as popen:
            assert popen.stdin
            popen.stdin.write(data)

            return popen.wait()

    filename = os.path.expanduser(filename)
    head = os.path.split(filename)[0]

    if head:
        os.makedirs(head, exist_ok=True)

    with open(filename, "wb") as myfile:
        return myfile.write(data)
