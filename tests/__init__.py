# pylint: disable=missing-docstring
import tempfile
from configparser import ConfigParser
from pathlib import Path
from typing import Any
from unittest import TestCase

from unittest_fixtures import given

from larry import config
from larry.color import Color
from larry.config import DEFAULT_INPUT_PATH

RASTER_IMAGE = (Path(__file__).parent / "test.png").read_bytes()
SVG_IMAGE = Path(DEFAULT_INPUT_PATH).read_bytes()
CSS = """\
a {
  color: #4a4a4a;
  background: rgb(51,51,51);
}

b {
  color: #3a7e94;
  background: rgba(0, 45, 108, 0.6);
}

c {
  color: rgb(58, 126, 148);
  background: #002d6c;
}

d {
  color: #333;
}
"""


def make_colors(colors: str) -> list[Color]:
    return [Color(s) for s in colors.split()]


def mock_write_file(bytes_io):
    def write_file(_filename: str, data: bytes):
        bytes_io.write(data)

    return write_file


def mock_write_text_file(bytes_io):
    def write_text_file(_filename: str, text: str, encoding: str = "utf8"):
        bytes_io.write(text.encode(encoding))

    return write_text_file


def make_config(name: str, section: str = "filters", **settings: Any) -> ConfigParser:
    _config = ConfigParser()
    section = f"{section}:{name}"
    _config.add_section(section)

    for key, value in settings.items():
        _config[section][key] = str(value)

    return _config
