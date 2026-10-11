"""Negative/positive tests of the offline simplified hard filter."""
import copy
import unittest
from examples.v02.scheduling_filter import assess, validate_case

BASE = {
    "nodes": [
        {
            "name": "worker-a", "zone": "a", "labels": {"pool": "apps"},
            "taints": [], "cpu_allocatable_m": 4000, "cpu_requested_m": 3500,
            "memory_allocatable_mib": 8192, "memory_requested_mib": 4096,
        },
        {
            "name": "worker-b", "zone": "b", "labels": {"pool": "apps"},
            "taints": ["reserved"], "cpu_allocatable_m": 8000,
            "cpu_requested_m": 4000,
            "memory_allocatable_mib": 16384, "memory_requested_mib": 10240,
        },
    ],
    "pod": {
        "cpu_m": 1000, "memory_mib": 1024,
        "node_selector": {"pool": "apps"}, "tolerations": [],
        "eligible_zones": [],
    }
}


class SchedulingFilterTests(unittest.TestCase):
    def copy(self):
        return copy.deepcopy(BASE)

    def test_baseline_unschedulable(self):
        out = assess(self.copy())
        self.assertEqual(out["eligible_nodes"], [])
        self.assertEqual(out["decisions"][0]["reasons"],
                         ["Insufficient CPU requests capacity"])
        self.assertEqual(out["decisions"][1]["reasons"], ["UntoleratedTaint"])

    def test_toleration_makes_b_eligible(self):
        case = self.copy()
        case["pod"]["tolerations"].append("reserved")
        self.assertEqual(assess(case)["eligible_nodes"], ["worker-b"])

    def test_reducing_requests_does_not_cancel_taint(self):
        case = self.copy()
        case["pod"]["cpu_m"] = 100
        self.assertEqual(assess(case)["eligible_nodes"], ["worker-a"])

    def test_insufficient_memory_reason(self):
        case = self.copy()
        case["nodes"][0]["cpu_requested_m"] = 0
        case["nodes"][0]["memory_requested_mib"] = 8000
        self.assertIn("Insufficient memory requests capacity",
                      assess(case)["decisions"][0]["reasons"])

    def test_selector_mismatch(self):
        case = self.copy()
        case["pod"]["node_selector"]["pool"] = "gpu"
        self.assertIn("NodeSelectorMismatch",
                      assess(case)["decisions"][0]["reasons"])

    def test_zone_excluded(self):
        case = self.copy()
        case["pod"]["tolerations"] = ["reserved"]
        case["pod"]["eligible_zones"] = ["a"]
        self.assertIn("ZoneExcluded",
                      assess(case)["decisions"][1]["reasons"])

    def test_empty_eligible_zones_means_no_zone_filter(self):
        case = self.copy()
        case["pod"]["tolerations"] = ["reserved"]
        self.assertEqual(assess(case)["eligible_nodes"], ["worker-b"])

    def test_report_disclaims_real_scheduler(self):
        out = assess(self.copy())
        self.assertTrue(out["not_a_real_scheduler"])
        self.assertEqual(out["model"], "OFFLINE_HARD_FILTER_ONLY")

    def test_equal_cpu_capacity_fits(self):
        case = self.copy()
        case["nodes"][0]["cpu_requested_m"] = 3000
        self.assertIn("worker-a", assess(case)["eligible_nodes"])

    def test_duplicate_node_rejected(self):
        case = self.copy()
        case["nodes"][1]["name"] = "worker-a"
        with self.assertRaises(ValueError):
            assess(case)

    def test_boolean_capacity_rejected(self):
        case = self.copy()
        case["nodes"][0]["cpu_allocatable_m"] = True
        with self.assertRaises(ValueError):
            assess(case)

    def test_negative_requests_rejected(self):
        case = self.copy()
        case["nodes"][1]["cpu_requested_m"] = -1
        with self.assertRaises(ValueError):
            assess(case)

    def test_requests_above_allocatable_rejected(self):
        case = self.copy()
        case["nodes"][0]["cpu_requested_m"] = 5000
        with self.assertRaises(ValueError):
            assess(case)

    def test_unknown_pod_field_rejected(self):
        case = self.copy()
        case["pod"]["secret"] = "bad"
        with self.assertRaises(ValueError):
            assess(case)

    def test_unknown_node_field_rejected(self):
        case = self.copy()
        case["nodes"][0]["token"] = "bad"
        with self.assertRaises(ValueError):
            assess(case)

    def test_missing_field_rejected(self):
        case = self.copy()
        del case["pod"]["tolerations"]
        with self.assertRaises(ValueError):
            assess(case)

    def test_wrong_selector_type_rejected(self):
        case = self.copy()
        case["pod"]["node_selector"] = ["apps"]
        with self.assertRaises(ValueError):
            assess(case)

    def test_invalid_taint_type_rejected(self):
        case = self.copy()
        case["nodes"][0]["taints"] = [42]
        with self.assertRaises(ValueError):
            assess(case)

    def test_too_many_nodes_rejected(self):
        case = self.copy()
        case["nodes"] = [self.copy()["nodes"][0] for _ in range(101)]
        with self.assertRaises(ValueError):
            assess(case)

    def test_function_does_not_mutate_input(self):
        case = self.copy()
        before = copy.deepcopy(case)
        assess(case)
        self.assertEqual(case, before)


if __name__ == "__main__":
    unittest.main()
