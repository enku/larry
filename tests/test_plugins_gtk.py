# pylint: disable=missing-docstring,unused-argument
import io
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry.plugins import gtk

from . import lib, make_colors, mock_write_text_file


@given(lib.random, lib.configmaker, lib.tmpdir)
@mock.patch("larry.plugins.gtk.write_text_file")
class GtkTests(TestCase):
    def test(self, write_text_file, fixtures: Fixtures) -> None:
        output = io.BytesIO()
        write_text_file.side_effect = mock_write_text_file(output)
        cssfile = f"{fixtures.tmpdir}/input.css"

        with open(cssfile, "w", encoding="UTF-8") as fp:
            fp.write(lib.CSS)

        configmaker = fixtures.configmaker
        configmaker.add_section("plugins:gtk")
        configmaker.add_config(template=cssfile, location="/dev/null")

        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        gtk.plugin(colors, configmaker.config["plugins:gtk"])

        expected = """\
a {
  color: #4a3441;
  background: rgb(51, 36, 45);
}

b {
  color: #943972;
  background: rgba(108, 0, 68, 0.6);
}

c {
  color: rgb(148, 57, 114);
  background: #6c0044;
}

d {
  color: #33242d;
}
"""
        self.assertEqual(output.getvalue(), expected.encode("UTF-8"))
