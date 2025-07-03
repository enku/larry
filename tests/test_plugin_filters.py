# pylint: disable=missing-docstring,unused-argument
from configparser import SectionProxy
from unittest import TestCase

from unittest_fixtures import Fixtures, fixture, given

from larry.color import ColorList
from larry.config import ConfigType
from larry.plugins import filtered, make_filter_config

from . import fixtures as tf
from .utils import make_colors

COLORS = make_colors("#177AFF #FF1500 #FF0278 #799FCF")


@fixture(tf.configmaker)
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

        self.assertEqual(colors, make_colors("#006ddb #db0000 #db006d #6d92b6"))

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
