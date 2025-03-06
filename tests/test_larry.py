# pylint: disable=missing-docstring
from unittest import TestCase

import larry
from larry import config


class ConfigTypeTests(TestCase):
    def test(self):
        with self.assertWarns(DeprecationWarning):
            config_type = larry.ConfigType

        self.assertIs(config_type, config.ConfigType)
