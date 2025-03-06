"""Test utilities"""

# pylint: disable=missing-docstring

from configparser import ConfigParser
from typing import IO, Any, Callable

from larry.color import Color


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]


def make_config(name: str, section: str = "filters", **settings: Any) -> ConfigParser:
    _config = ConfigParser()
    section = f"{section}:{name}"
    _config.add_section(section)

    for key, value in settings.items():
        _config[section][key] = str(value)

    return _config


def mock_write_file(bytes_io: IO[bytes]) -> Callable[[Any, bytes], None]:
    def write_file(_filename: str, data: bytes):
        bytes_io.write(data)

    return write_file


def mock_write_text_file(bytes_io: IO[bytes]) -> Callable[[Any, str, str], None]:
    def write_text_file(_filename: str, text: str, encoding: str = "utf8"):
        bytes_io.write(text.encode(encoding))

    return write_text_file
