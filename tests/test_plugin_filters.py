# pylint: disable=missing-docstring,unused-argument
from configparser import SectionProxy
from unittest import TestCase

from unittest_fixtures import Fixtures, fixture, given

from larry.color import ColorList
from larry.config import ConfigType
from larry.io import read_file
from larry.plugins import do_plugin, filtered, make_filter_config

from . import lib

COLORS = lib.make_colors("#177AFF #FF1500 #FF0278 #799FCF")


@fixture(lib.configmaker)
def section(fixtures: Fixtures) -> SectionProxy:
    configmaker = fixtures.configmaker
    configmaker.add_section("plugins:test")

    return configmaker.config["plugins:test"]


@filtered
def plugin(colors: ColorList, _config: ConfigType) -> ColorList:
    return colors


@given(config=section)
class FilteredPluginTests(TestCase):
    def test_none(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filter"] = "none"

        colors = plugin(COLORS, config)

        self.assertEqual(colors, COLORS)

    def test_inverse(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filter"] = "inverse"

        colors = plugin(COLORS, config)

        self.assertEqual(colors, [i.inverse() for i in COLORS])

    def test_with_filter_config(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filter"] = "vga"
        config["filters:vga:bits"] = "7"

        colors = plugin(COLORS, config)

        self.assertEqual(colors, lib.make_colors("#006ddb #db0000 #db006d #6d92b6"))

    def test_multiple_filters(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filter"] = "inverse pastelize"

        colors = plugin(COLORS, config)

        self.assertEqual(colors, [i.inverse().pastelize() for i in COLORS])


@given(config=section)
class MakeFilterConfigTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filters:vga:bits"] = "7"
        config["filters:other:bits"] = "19"

        filter_config = make_filter_config("vga", config)
        self.assertEqual(filter_config["filters:vga"]["bits"], "7")

        filter_config = make_filter_config("other", config)
        self.assertEqual(filter_config["filters:other"]["bits"], "19")


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
