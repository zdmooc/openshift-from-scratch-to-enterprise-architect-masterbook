import json
import unittest
from examples.v02.quorum_model import majority, assess, validate_case


def case(members=None, lost=None):
    return {
        "members": members or [
            {"id": "a", "zone": "x"},
            {"id": "b", "zone": "y"},
            {"id": "c", "zone": "z"},
        ],
        "lost_zones": [] if lost is None else lost,
    }


class QuorumModelTests(unittest.TestCase):
    def test_majority_one(self):
        self.assertEqual(majority(1), 1)
    def test_majority_three(self):
        self.assertEqual(majority(3), 2)
    def test_majority_four(self):
        self.assertEqual(majority(4), 3)
    def test_majority_five(self):
        self.assertEqual(majority(5), 3)
    def test_noninteger_rejected(self):
        with self.assertRaises(ValueError):
            majority(True)
    def test_three_members_one_zone_lost(self):
        self.assertTrue(assess(case(lost=["x"]))["majority_possible"])
    def test_three_members_two_zones_lost(self):
        self.assertFalse(assess(case(lost=["x", "y"]))["majority_possible"])
    def test_correlated_failure_of_two_members(self):
        data = case(members=[
            {"id": "a", "zone": "rack-a"},
            {"id": "b", "zone": "rack-a"},
            {"id": "c", "zone": "rack-b"},
        ], lost=["rack-a"])
        self.assertFalse(assess(data)["majority_possible"])
    def test_duplicate_members_rejected(self):
        with self.assertRaises(ValueError):
            assess(case(members=[
                {"id": "a", "zone": "x"},
                {"id": "a", "zone": "y"},
            ]))
    def test_unknown_zone_rejected(self):
        with self.assertRaises(ValueError):
            assess(case(lost=["unknown"]))
    def test_duplicate_zones_rejected(self):
        with self.assertRaises(ValueError):
            assess(case(lost=["x", "x"]))
    def test_schema_extra_key_rejected(self):
        obj = case(); obj["credentials"] = "forbidden"
        with self.assertRaises(ValueError):
            assess(obj)
    def test_empty_members_rejected(self):
        with self.assertRaises(ValueError):
            assess({"members": [], "lost_zones": []})
    def test_bool_as_zone_rejected(self):
        with self.assertRaises(ValueError):
            assess(case(lost=[True]))
    def test_not_runtime_proof_marker(self):
        self.assertTrue(assess(case())["not_runtime_proof"])
    def test_no_majority_does_not_trigger_mutation(self):
        self.assertFalse(assess(case(lost=["x","y"]))["majority_possible"])
        self.assertEqual(set(assess(case()).keys()), {
            "model","voters","majority","available_voters",
            "unavailable_voters","majority_possible","lost_zones",
            "not_runtime_proof","warnings"
        })


if __name__ == "__main__":
    unittest.main()
