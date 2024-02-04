# pylint: disable=missing-docstring
import random
from unittest import mock

from larry import utils

from . import TestCase


class Between(TestCase):
    def test_true(self):
        self.assertTrue(utils.between(0.4, 0, 1))

    def test_false(self):
        self.assertFalse(utils.between(-0.4, 0, 1))


class ParseRange(TestCase):
    def test_ints(self):
        self.assertEqual(utils.parse_range("1 2"), (1, 2))

    def test_float_and_int_returns_floats(self):
        t = utils.parse_range("1.5 2")
        self.assertEqual(t, (1.5, 2.0))

        self.assertTrue(isinstance(t[0], float))
        self.assertTrue(isinstance(t[1], float))

    def test_int_and_float_returns_floats2(self):
        t = utils.parse_range("1 2.5")
        self.assertEqual(t, (1.0, 2.5))

        self.assertTrue(isinstance(t[0], float))
        self.assertTrue(isinstance(t[1], float))

    def test_float_and_float_returns_floats(self):
        t = utils.parse_range("1.5 2.5")
        self.assertEqual(t, (1.5, 2.5))

        self.assertTrue(isinstance(t[0], float))
        self.assertTrue(isinstance(t[1], float))

    def test_negative(self):
        self.assertEqual(utils.parse_range("-10 -5"), (-10, -5))

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            utils.parse_range("-5 -10")

    def test_extra_spaces(self):
        self.assertEqual(utils.parse_range(" -10   -5	"), (-10, -5))


@mock.patch("larry.utils.random", random.Random(1706558124))
class RandsignTests(TestCase):
    def test(self):
        self.assertEqual(utils.randsign(4), 4)
        self.assertEqual(utils.randsign(4), 0)
        self.assertEqual(utils.randsign(100), -19)


class ClipTests(TestCase):
    def test1(self):
        self.assertEqual(utils.clip(20), 20)

    def test2(self):
        self.assertEqual(utils.clip(-20), 0)

    def test3(self):
        self.assertEqual(utils.clip(20, maximum=19), 19)

    def test4(self):
        self.assertEqual(utils.clip(-20, minimum=-4), -4)

    def test5(self):
        self.assertEqual(utils.clip(300), 255)

    def test6(self):
        self.assertEqual(utils.clip(-3), 0)


class AngularDistanceTests(TestCase):
    def test_simple(self):
        self.assertEqual(utils.angular_distance(270, 360), 90)
        self.assertEqual(utils.angular_distance(270, 0), 90)

    def test_single_wrap(self):
        self.assertAlmostEqual(utils.angular_distance(270, 1), 91)

    def test_multi_wrap(self):
        self.assertAlmostEqual(utils.angular_distance(270, 990), 0)


class BucketsTest(TestCase):
    def test(self):
        start = 0
        stop = 10
        step = 2

        self.assertEqual(
            utils.buckets(start, stop, step), [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10)]
        )
