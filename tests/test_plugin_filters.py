# pylint: disable=missing-docstring,unused-argument
from configparser import SectionProxy
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, fixture, given

from larry.plugins import filtered, make_filter_config, parse_filter_string

from .utils import make_colors

COLORS = make_colors("#177AFF #FF1500 #FF0278 #799FCF")


@fixture("configmaker")
def section(fixtures: Fixtures) -> SectionProxy:
    configmaker = fixtures.configmaker
    configmaker.add_section("plugins:test")

    return configmaker.config["plugins:test"]


@fixture()
def plugin_fixture(_fixtures: Fixtures) -> mock.Mock:
    return mock.Mock(name="plugin")


@given(plugin_fixture, config=section)
class FilteredPluginTests(TestCase):
    def test_none(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config["filter"] = "none"
        plugin = fixtures.plugin
        filtered_plugin = filtered(plugin)

        filtered_plugin(COLORS, config)

        plugin.assert_called_once_with(COLORS, config)

    def test_inverse(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        plugin = fixtures.plugin
        config["filter"] = "inverse"
        filtered_plugin = filtered(plugin)

        filtered_plugin(COLORS, config)

        plugin.assert_called_once_with([i.inverse() for i in COLORS], config)

    def test_with_filter_config(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        plugin = fixtures.plugin
        config["filter"] = "vga"
        config["filters:vga:bits"] = "7"
        filtered_plugin = filtered(plugin)

        filtered_plugin(COLORS, config)

        plugin.assert_called_once_with(
            make_colors("#006ddb #db0000 #db006d #6d92b6"), config
        )

    def test_multiple_filters(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        plugin = fixtures.plugin
        config["filter"] = "inverse pastelize"
        filtered_plugin = filtered(plugin)

        filtered_plugin(COLORS, config)

        plugin.assert_called_once_with(
            [i.inverse().pastelize() for i in COLORS], config
        )


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


class ParseFilterString(TestCase):
    def test(self) -> None:
        self.assertEqual([], parse_filter_string("none"))
        self.assertEqual([], parse_filter_string(""))
        self.assertEqual([], parse_filter_string(" "))
        self.assertEqual(["inverse", "vga"], parse_filter_string("inverse vga "))
