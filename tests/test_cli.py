# pylint: disable=missing-docstring
import argparse
import contextlib
import io
import os.path
import signal
from unittest import TestCase, mock

from unittest_fixtures import Fixtures, given

from larry import cli, filters
from larry.image import make_image_from_bytes
from larry.io import read_file

from . import make_colors


class HandlerTests(TestCase):
    def tearDown(self):
        cli.Handler.set(None)
        super().tearDown()

    def test(self):
        self.assertEqual(cli.Handler.get(), None)

        cli.Handler.set(6)
        self.assertEqual(cli.Handler.get(), 6)


class ParseArgsTests(TestCase):
    def test(self):
        argv = ["-c", "/dev/null", "--list-filters", "-n2"]
        args = cli.parse_args(argv)

        expected = argparse.Namespace(
            config_path="/dev/null",
            debug=False,
            interval=2,
            list_filters=True,
            list_plugins=False,
        )
        self.assertEqual(args, expected)


@given("config")
class RunTests(TestCase):
    def test_runs_filters_and_schedules_plugins(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_config(plugins="command dummy", filter="inverse pastelize")

        loop = mock.Mock()
        cli.run(config.path, loop)

        self.assertTrue(os.path.exists(config.config["larry"]["output"]))
        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        loop.call_soon.assert_has_calls(
            [
                mock.call(cli.do_plugin, "command", colors, config.path),
                mock.call(cli.do_plugin, "dummy", colors, config.path),
            ]
        )

    def test_pause_mode_does_nothing(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_config(
            pause="1", plugins="command dummy", filter="inverse pastelize"
        )

        loop = mock.Mock()
        cli.run(config.path, loop)

        self.assertFalse(os.path.exists(config.config["larry"]["output"]))
        loop.call_soon.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_logs_invalid_filters(self, logger, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_config(filter="inverse bogus pastelize")

        loop = mock.Mock()
        cli.run(config.path, loop)

        logger.exception.assert_called_once_with(
            "Color filter bogus not found. Skipping."
        )

        pastelize = filters.load_filter("pastelize")
        inverse = filters.load_filter("inverse")
        colors = pastelize(
            inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        image = make_image_from_bytes(read_file(config.config["larry"]["output"]))
        image_colors = image.get_colors()
        self.assertEqual(set(colors), set(image_colors))

    def test_colors_from_config(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        color_str = "red white blue pink yellow"
        config.add_config(colors=color_str, filter="none")

        loop = mock.Mock()
        cli.run(config.path, loop)

        image = make_image_from_bytes(read_file(config.config["larry"]["output"]))
        image_colors = image.get_colors()
        colors = make_colors(color_str)
        self.assertEqual(set(colors), set(image_colors))

    def test_run_with_no_config(self, fixtures: Fixtures) -> None:
        with mock.patch("larry.cli.write_file") as write_file:
            cli.run(f"{fixtures.tmpdir}/bogus.cfg", mock.Mock())

        write_file.assert_called()


@given("config")
class RunEveryTests(TestCase):
    def test_runs_and_schedules_to_run_again(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(15.0, config.path, loop)

        self.assertTrue(os.path.exists(config.config["larry"]["output"]))
        loop.call_later.assert_called_once_with(
            15.0, cli.run_every, 15.0, config.path, loop
        )
        timer_handler = loop.call_later.return_value
        mock_handler.set_assert_called_once_with(timer_handler)

    def test_runs_only_once_with_interval_0(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(0, config.path, loop)

        loop.call_later.assert_not_called()

    def test_cancel_existing_handler(self, fixtures: Fixtures) -> None:
        config = fixtures.config
        with mock.patch("larry.cli.Handler") as mock_handler:
            handler = mock.Mock()
            mock_handler.get.return_value = handler
            loop = mock.Mock()
            cli.run_every(15.0, config.path, loop)

        handler.cancel.assert_called_once_with()


@given("config")
@mock.patch("larry.cli.asyncio.new_event_loop")
class MainTests(TestCase):
    def test(self, new_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        argv = f"larry -c {config.path} --interval=60".split()

        cli.main(argv)

        loop = new_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run_every, 60, config.path, loop
        )
        loop.call_soon.assert_called_once_with(cli.run_every, 60, config.path, loop)
        loop.run_forever.assert_called_once_with()
        loop.close.assert_called_once_with()

    def test_with_interval_0(self, new_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        argv = f"larry -c {config.path} -n0".split()

        cli.main(argv)

        loop = new_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run, config.path, loop
        )

    def test_keyboard_interrupt_stops_loop(
        self, new_event_loop, fixtures: Fixtures
    ) -> None:
        config = fixtures.config
        argv = f"larry -c {config.path} --interval 60".split()
        loop = new_event_loop.return_value
        loop.run_forever.side_effect = KeyboardInterrupt()

        cli.main(argv)

        loop.stop.assert_called_once_with()

    def test_list_plugins(self, new_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        config.add_config(plugins="command")
        argv = f"larry -c {config.path} --list-plugins".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        self.assertIn("[X] command", stdout.getvalue())
        new_event_loop.assert_not_called()

    def test_list_filters(self, new_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        argv = f"larry -c {config.path} --list-filters".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        self.assertIn("[X] gradient", stdout.getvalue())
        new_event_loop.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_with_debug(self, logger, _new_event_loop, fixtures: Fixtures) -> None:
        config = fixtures.config
        argv = f"larry -c {config.path} --debug --list-plugins".split()

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.main(argv)

        logger.setLevel.assert_called_once_with("DEBUG")
