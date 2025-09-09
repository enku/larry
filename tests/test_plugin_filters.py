# pylint: disable=missing-docstring
from unittest import TestCase

from unittest_fixtures import Fixtures, given

from larry.io import read_file
from larry.plugins import do_plugin

from . import lib


@given(lib.configmaker, lib.tmpdir)
class PluginFilterTest(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        output_file = f"{fixtures.tmpdir}/test.txt"
        configmaker.add_config(plugins="command")
        configmaker.add_section("plugins:command")
        command_config = {
            "command": f"cat > {output_file}",
            "filter": "inverse neonize",
            "filter.neonize.brightness": "50",
        }
        configmaker.add_config(**command_config)
        colors = lib.make_colors("#ff0000 #ffffff #0000ff")

        do_plugin("command", colors, configmaker.path)

        output = read_file(output_file)
        self.assertEqual(output, b"#007f7f\n#7f0002\n#7f7f00")
