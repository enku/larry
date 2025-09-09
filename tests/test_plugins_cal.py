# pylint: disable=missing-docstring,unused-argument
import io
from configparser import ConfigParser
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry.plugins import cal

from . import lib


@given(lib.random)
@mock.patch("larry.plugins.cal.io.write_file")
class CalTests(TestCase):
    def test(self, write_file, fixtures: Fixtures):
        output = io.BytesIO()
        write_file.side_effect = lib.mock_write_file(output)
        colors = lib.make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        config = ConfigParser()
        config.add_section("plugins:cal")
        config.set("plugins:cal", "filter", "pastelize")

        cal.plugin(colors, config["plugins:cal"])

        expected = """\
today 38;1;255;127;208
weeknumber 38;2;166;127;255
header 38;2;237;127;255
workday 38;2;127;247;255
weekend 38;2;255;236;127
"""
        self.assertEqual(output.getvalue(), expected.encode("UTF-8"))
