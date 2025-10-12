# pylint: disable=missing-docstring,unused-argument
from unittest import IsolatedAsyncioTestCase, TestCase, mock

from unittest_fixtures import Fixtures, given

from larry import plugins
from larry.io import read_file
from larry.plugins import command

from . import lib


@given(lib.configmaker, lib.tmpdir)
class DoPluginTest(IsolatedAsyncioTestCase):
    async def test(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        plugin = "command"
        output_file = f"{fixtures.tmpdir}/test.txt"
        configmaker.add_config(plugins=plugin)
        configmaker.add_section("plugins:command")
        configmaker.add_config(command=f"cat > {output_file}")
        colors = lib.make_colors("#ff0000 #ffffff #0000ff")

        await plugins.do_plugin(plugin, colors, configmaker.path)

        output = read_file(output_file)
        self.assertEqual(output, b"#ff0000\n#ffffff\n#0000ff")

    async def test_without_coroutine(self, fixtures: Fixtures) -> None:
        called = False
        colors = lib.make_colors("#ff0000 #ffffff #0000ff")
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="fake_plugin")

        def fake_plugin(_colors, _config):
            nonlocal called
            called = True

        with mock.patch("larry.plugins.load", return_value=fake_plugin):
            with self.assertLogs("larry", level="WARNING") as log:
                await plugins.do_plugin("fake_plugin", colors, configmaker.path)

        self.assertTrue(called)
        self.assertIn("WARNING:larry:plugin fake_plugin not asynchronous", log.output)

    async def test_when_plugin_raises_exception(self, fixtures: Fixtures):
        async def fake_plugin(_colors, _config):
            raise RuntimeError("I failed")

        with mock.patch("larry.plugins.load", return_value=fake_plugin):
            with self.assertLogs("larry", level="ERROR") as log:
                await plugins.do_plugin("fake_plugin", [], "")

        error = log.output[-1]
        self.assertIn("ERROR:larry:Error running plugin fake_plugin", error)


class PluginsList(TestCase):
    def test(self):
        lst = plugins.plugins_list()

        self.assertTrue(lst)
        for item in lst:
            self.assertTrue(isinstance(item[0], str))
            self.assertTrue(callable(item[1]))


@given(lib.configmaker)
class ListPlugins(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        configmaker = fixtures.configmaker
        configmaker.add_config(plugins="command vim")

        output = plugins.list_plugins(configmaker.path)

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
