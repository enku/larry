# pylint: disable=missing-docstring
import io
import random
from unittest import mock

from larry.plugins import gtk

from . import CSS, ConfigTestCase, make_colors, mock_write_file


@mock.patch("larry.color.random", random.Random(1))
@mock.patch("larry.plugins.gtk.write_file")
class GtkTests(ConfigTestCase):
    def test(self, write_file):
        output = io.BytesIO()
        write_file.side_effect = mock_write_file(output)
        cssfile = f"{self.tmpdir}/input.css"

        with open(cssfile, "w", encoding="UTF-8") as fp:
            fp.write(CSS)

        self.add_section("plugins:gtk")
        self.add_config(template=cssfile, location="/dev/null")

        colors = make_colors(
            "#7e118f #754fc7 #835d75 #807930 #9772ea #9f934b #39e822 #35dfe9"
        )
        gtk.plugin(colors, self.config["plugins:gtk"])

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
