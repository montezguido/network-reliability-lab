import unittest

from network_reliability.incidents import current_snapshot, transitions
from network_reliability.models import CheckResult


def result(name, state):
    return CheckResult(name, state, "tcp", 0.5, "synthetic")


class IncidentTests(unittest.TestCase):
    def test_initial_up_is_not_incident(self):
        self.assertEqual(transitions({}, [result("one", "UP")]), [])

    def test_initial_down_opens(self):
        events = transitions({}, [result("one", "DOWN")])
        self.assertEqual(events[0].event, "OPENED")
        self.assertIsNone(events[0].previous)

    def test_repeated_down_does_not_duplicate(self):
        self.assertEqual(transitions({"one": "DOWN"}, [result("one", "DOWN")]), [])

    def test_change_up_to_down(self):
        events = transitions({"one": "UP"}, [result("one", "DOWN")])
        self.assertEqual(events[0].event, "OPENED")

    def test_down_to_up_recovers(self):
        events = transitions({"one": "DOWN"}, [result("one", "UP")])
        self.assertEqual(events[0].event, "RECOVERED")

    def test_invalid_result_state_is_rejected(self):
        with self.assertRaises(ValueError):
            transitions({}, [result("one", "UNKNOWN")])

    def test_snapshot(self):
        self.assertEqual(current_snapshot([result("a", "UP"), result("b", "DOWN")]),
                         {"a": "UP", "b": "DOWN"})
