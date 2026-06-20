import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.state import new_state, step_percent, STEP_WEIGHTS


class TestNewState(unittest.TestCase):
    def test_fields(self):
        s = new_state()
        self.assertEqual(s["percent"], 0)
        self.assertEqual(s["step"], "")
        self.assertFalse(s["done"])
        self.assertIsNone(s["error"])


class TestStepWeights(unittest.TestCase):
    def test_sum_to_100(self):
        self.assertEqual(sum(STEP_WEIGHTS), 100)


class TestStepPercent(unittest.TestCase):
    def test_first_step_zero_sub(self):
        self.assertEqual(step_percent(0, 0), 0)

    def test_first_step_full(self):
        self.assertEqual(step_percent(0, 100), STEP_WEIGHTS[0])

    def test_last_step_full(self):
        self.assertEqual(step_percent(len(STEP_WEIGHTS) - 1, 100), 100)

    def test_mid_step(self):
        prior = sum(STEP_WEIGHTS[:2])
        half = STEP_WEIGHTS[2] * 0.5
        self.assertEqual(step_percent(2, 50), int(prior + half))


if __name__ == "__main__":
    unittest.main()
