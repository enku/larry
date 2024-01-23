# pylint: disable=missing-docstring
import io
import os.path

from larry import config

from . import TestCase


class LoadTomlConfig(TestCase):
    def test(self):
        toml = """\
[inventory]

[inventory.main]
name = "vase"
value = 26
colors = ["red", "green", "blue"]
"""
        path = os.path.join(self.tmpdir, "test.toml")
        with open(path, "w") as fp:
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
