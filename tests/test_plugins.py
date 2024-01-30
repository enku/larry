# pylint: disable=missing-docstring
from larry import plugins
from larry.io import read_file
from larry.plugins import command

from . import ConfigTestCase, TestCase, make_colors


class DoPluginTest(ConfigTestCase):
    def test(self):
        plugin = "command"
        output_file = f"{self.tmpdir}/test.txt"
        self.add_config(plugins=plugin)
        self.add_section("plugins:command")
        self.add_config(command=f"cat > {output_file}")
        colors = make_colors("#ff0000 #ffffff #0000ff")

        plugins.do_plugin(plugin, colors, self.config_path)

        output = read_file(output_file)
        self.assertEqual(output, b"#ff0000\n#ffffff\n#0000ff")


class PluginsList(TestCase):
    def test(self):
        lst = plugins.plugins_list()

        self.assertTrue(lst)
        for item in lst:
            self.assertTrue(isinstance(item[0], str))
            self.assertTrue(callable(item[1]))


class ListPlugins(ConfigTestCase):
    def test(self):
        self.add_config(plugins="command vim")

        output = plugins.list_plugins(self.config_path)

        self.assertIn("[X] command", output)
        self.assertIn("[X] vim", output)
        self.assertIn("[ ] gtk", output)


class LoadTests(TestCase):
    def test(self):
        plugin = plugins.load("command")

        self.assertIs(plugin, command.plugin)

    def test_plugin_not_found(self):
        with self.assertRaises(plugins.PluginNotFound):
            plugins.load("bogus")
