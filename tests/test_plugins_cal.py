# pylint: disable=missing-docstring
import io
import random
from unittest import mock

from larry.plugins import cal

from . import ConfigTestCase, make_colors, mock_write_file


@mock.patch("larry.color.random", random.Random(1))
@mock.patch("larry.plugins.cal.io.write_file")
class CalTests(ConfigTestCase):
    def test(self, write_file):
        output = io.BytesIO()
        write_file.side_effect = mock_write_file(output)
        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )

        cal.plugin(colors, None)

        expected = """\
today 38;1;255;127;208
weeknumber 38;2;166;127;255
header 38;2;237;127;255
workday 38;2;127;247;255
weekend 38;2;255;236;127
"""
        self.assertEqual(output.getvalue(), expected.encode("UTF-8"))
