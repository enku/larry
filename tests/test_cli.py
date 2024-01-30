# pylint: disable=missing-docstring
import argparse
import contextlib
import io
import os.path
import signal
from unittest import mock

from larry import cli, filters, make_image_from_bytes
from larry.io import read_file

from . import TestCase as BaseTestCase
from . import make_colors


class TestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        config = f"""\
[larry]
output = {self.tmpdir}/larry.svg
"""
        self.config_path = f"{self.tmpdir}/larry.cfg"
        with open(self.config_path, "w", encoding="UTF-8") as fp:
            fp.write(config)

    def add_config(self, **kwargs):
        with open(self.config_path, "a", encoding="UTF-8") as config_file:
            for name, value in kwargs.items():
                print(f"{name} = {value}", file=config_file)


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
        argv = ["-c", "/dev/null", "--list-filters", "--daemonize", "-n2"]
        args = cli.parse_args(argv)

        expected = argparse.Namespace(
            config_path="/dev/null",
            daemonize=True,
            debug=False,
            interval=2,
            list_filters=True,
            list_plugins=False,
        )
        self.assertEqual(args, expected)


@mock.patch("larry.cli.asyncio.get_event_loop")
class RunTests(TestCase):
    def test_runs_filters_and_schedules_plugins(self, get_event_loop):
        self.add_config(plugins="command dummy", filter="inverse pastelize")

        cli.run(self.config_path)

        self.assertTrue(os.path.exists(f"{self.tmpdir}/larry.svg"))
        loop = get_event_loop.return_value
        colors = filters.pastelize(
            filters.inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        loop.call_soon.assert_has_calls(
            [
                mock.call(cli.do_plugin, "command", colors, self.config_path),
                mock.call(cli.do_plugin, "dummy", colors, self.config_path),
            ]
        )

    def test_pause_mode_does_nothing(self, get_event_loop):
        self.add_config(pause="1", plugins="command dummy", filter="inverse pastelize")

        cli.run(self.config_path)

        self.assertFalse(os.path.exists(f"{self.tmpdir}/larry.svg"))
        loop = get_event_loop.return_value
        loop.call_soon.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_logs_invalid_filters(self, logger, _get_event_loop):
        self.add_config(filter="inverse bogus pastelize")

        cli.run(self.config_path)

        logger.exception.assert_called_once_with(
            "Color filter bogus not found. Skipping."
        )

        colors = filters.pastelize(
            filters.inverse(
                make_colors("#000000 #1c343f #254351 #666666 #7c8e96 #ffffff"), None
            ),
            None,
        )
        image = make_image_from_bytes(read_file(f"{self.tmpdir}/larry.svg"))
        image_colors = image.get_colors()
        self.assertEqual(set(colors), set(image_colors))

    def test_colors_from_config(self, _get_event_loop):
        color_str = "red white blue pink yellow orange"
        self.add_config(colors=color_str, filter="none")

        cli.run(self.config_path)

        image = make_image_from_bytes(read_file(f"{self.tmpdir}/larry.svg"))
        image_colors = image.get_colors()
        colors = make_colors(color_str)
        self.assertEqual(set(colors), set(image_colors))

    def test_run_with_no_config(self, _get_event_loop):
        with mock.patch("larry.cli.write_file") as write_file:
            cli.run(f"{self.tmpdir}/bogus.cfg")

        write_file.assert_called()


class RunEveryTests(TestCase):
    def test_runs_and_schedules_to_run_again(self):
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(15.0, self.config_path, loop)

        self.assertTrue(os.path.exists(f"{self.tmpdir}/larry.svg"))
        loop.call_later.assert_called_once_with(
            15.0, cli.run_every, 15.0, self.config_path, loop
        )
        timer_handler = loop.call_later.return_value
        mock_handler.set_assert_called_once_with(timer_handler)

    def test_runs_only_once_with_interval_0(self):
        with mock.patch("larry.cli.Handler") as mock_handler:
            mock_handler.get.return_value = None
            loop = mock.Mock()
            cli.run_every(0, self.config_path, loop)

        loop.call_later.assert_not_called()

    def test_cancel_existing_handler(self):
        with mock.patch("larry.cli.Handler") as mock_handler:
            handler = mock.Mock()
            mock_handler.get.return_value = handler
            loop = mock.Mock()
            cli.run_every(15.0, self.config_path, loop)

        handler.cancel.assert_called_once_with()


@mock.patch("larry.cli.real_main")
@mock.patch("larry.cli.daemon.DaemonContext")
class MainTests(TestCase):
    def test_daemonize_false(self, daemon, real_main):
        args = []
        cli.main(args)

        daemon.assert_not_called()
        real_main.assert_called_once_with(cli.parse_args(args))

    def test_daemonize_true(self, daemon, real_main):
        args = ["-d"]
        cli.main(args)

        daemon.assert_called_once_with()
        real_main.assert_called_once_with(cli.parse_args(args))


@mock.patch("larry.cli.asyncio.new_event_loop")
class RealMainTests(TestCase):
    def test(self, new_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=60,
            list_filters=False,
            list_plugins=False,
        )

        cli.real_main(args)

        loop = new_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run_every, args.interval, args.config_path, loop
        )
        loop.call_soon.assert_called_once_with(
            cli.run_every, args.interval, args.config_path, loop
        )
        loop.run_forever.assert_called_once_with()
        loop.close.assert_called_once_with()

    @mock.patch("larry.cli.asyncio.get_event_loop")
    def test_with_interval_0(self, _new_event_loop, get_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=0,
            list_filters=False,
            list_plugins=False,
        )

        cli.real_main(args)

        loop = get_event_loop.return_value
        loop.add_signal_handler.assert_called_once_with(
            signal.SIGUSR1, cli.run, args.config_path
        )

    def test_keyboard_interrupt_stops_loop(self, new_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            interval=60,
            list_filters=False,
            list_plugins=False,
        )
        loop = new_event_loop.return_value
        loop.run_forever.side_effect = KeyboardInterrupt()

        cli.real_main(args)

        loop.stop.assert_called_once_with()

    def test_list_plugins(self, new_event_loop):
        self.add_config(plugins="command")
        args = argparse.Namespace(
            config_path=self.config_path, debug=False, list_plugins=True
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        self.assertIn("[X] command", stdout.getvalue())
        new_event_loop.assert_not_called()

    def test_list_filters(self, new_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path,
            debug=False,
            list_plugins=False,
            list_filters=True,
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        self.assertIn("[X] gradient", stdout.getvalue())
        new_event_loop.assert_not_called()

    @mock.patch("larry.cli.LOGGER")
    def test_with_debug(self, logger, _new_event_loop):
        args = argparse.Namespace(
            config_path=self.config_path, debug=True, list_plugins=True
        )

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            cli.real_main(args)

        logger.setLevel.assert_called_once_with("DEBUG")
