# pylint: disable=missing-docstring
import io
import os.path
from configparser import ConfigParser
from unittest import TestCase

from unittest_fixtures import Fixtures, given

from larry import config


@given("tmpdir")
class LoadTests(TestCase):
    def test_when_file_does_not_exist(self, fixtures: Fixtures) -> None:
        path = os.path.join(fixtures.tmpdir, "bogus")
        config_obj = config.load(path)

        self.assertIn("input", config_obj["DEFAULT"])

    def test_loads_toml(self, fixtures: Fixtures) -> None:
        toml = """\
title = "test"

[inventory.main]
name = "vase"
value = 26
colors = ["red", "green", "blue"]
"""
        path = os.path.join(fixtures.tmpdir, "test.toml")
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(toml)

        config_obj = config.load(path)

        self.assertEqual(config_obj["inventory.main"]["value"], "26")


@given("tmpdir")
class GetPluginConfigTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        path = os.path.join(fixtures.tmpdir, "larry.cfg")
        config_str = """\
[plugins:test]
foo = bar
"""
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(config_str)

        plugin_config = config.get_plugin_config("test", path)
        self.assertEqual(plugin_config["foo"], "bar")

        plugin_config = config.get_plugin_config("bogus", path)  # shouldn't fail
        self.assertNotIn("foo", plugin_config)


@given("tmpdir")
class LoadTomlConfig(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        toml = """\
[inventory]

[inventory.main]
name = "vase"
value = 26
colors = ["red", "green", "blue"]
"""
        path = os.path.join(fixtures.tmpdir, "test.toml")
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(toml)

        result = config.load_toml_config(path)

        result_str = io.StringIO()
        result.write(result_str)

        expected = """\

[inventory]

[inventory.main]
name = vase
value = 26
colors = red
	green
	blue

"""
        self.assertTrue(result_str.getvalue().endswith(expected))


class ConfigFromTomlTests(TestCase):
    def test(self):
        toml = {
            "main": {"name": "vase", "value": 26, "colors": ["red", "green", "blue"]}
        }

        result = config.config_from_toml(toml)
        result_str = io.StringIO()
        result.write(result_str)

        expected = """\

[main]
name = vase
value = 26
colors = red
	green
	blue

"""
        self.assertTrue(result_str.getvalue().endswith(expected))


class StrFromTableTests(TestCase):
    def test(self):
        table = {
            "main": {"name": "vase", "value": 26, "colors": ["red", "green", "blue"]}
        }

        result = config.str_from_table("inventory", table)

        expected = """\
[inventory]

[inventory.main]
name = vase
value = 26
colors = red
    green
    blue
"""
        self.assertEqual(result, expected)


class StrFromConfigValueTests(TestCase):
    def test_string(self):
        value = "this is a test"

        result = config.str_from_config_value(value)

        self.assertEqual(result, value)

    def test_list(self):
        value = ["this", "is", "a", "test"]

        result = config.str_from_config_value(value)

        self.assertEqual(result, "this\n    is\n    a\n    test")

    def test_list_with_newlines(self):
        # is this even possible?
        value = ["this", "is", "a\n", "test"]

        result = config.str_from_config_value(value)

        # I'm not sure what this should equal, but I'm also not sure this is ever going
        # to happen
        self.assertEqual(result, "this\n    is\n    a\n\n    test")


class IsPausedTests(TestCase):
    def test_empty_config(self):
        my_config = ConfigParser()
        my_config.update({"larry": {}})
        self.assertFalse(config.is_paused(my_config))

    def test_config_set_true(self):
        my_config = ConfigParser()
        my_config.update({"larry": {"pause": "1"}})

        self.assertTrue(config.is_paused(my_config))

    def test_config_set_false(self):
        my_config = ConfigParser()
        my_config.update({"larry": {"pause": "0"}})

        self.assertFalse(config.is_paused(my_config))
