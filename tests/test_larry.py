# pylint: disable=missing-docstring
import larry
from larry import config

from . import TestCase


class ConfigTypeTests(TestCase):
    def test(self):
        with self.assertWarns(DeprecationWarning):
            config_type = larry.ConfigType

        self.assertIs(config_type, config.ConfigType)
