import json
import unittest

from examples.v01.n3_triage import MAX_BYTES, diagnose, parse_case, report


BASE = {
    "case_id": "LAB", "service": "reader", "desired_replicas": 2,
    "ready_replicas": 2, "ready_endpoints": 2, "pod_phase": "Running",
    "last_event_reason": "None", "pvc_phase": "NotApplicable",
    "dns_operator": "Available", "route_present": False,
    "service_selector_matches": True, "network_policy_present": False,
}


def codes(**overrides):
    data = {**BASE, **overrides}
    parsed = parse_case(json.dumps(data))
    return [f.code for f in diagnose(parsed)]


class TriageTests(unittest.TestCase):
    def test_no_ready_endpoints(self):
        self.assertIn("NO_READY_ENDPOINTS", codes(ready_endpoints=0))
    def test_ready_but_not_desired(self):
        self.assertIn("REPLICAS_UNAVAILABLE", codes(ready_replicas=1))
    def test_pending_pod(self):
        self.assertIn("POD_PENDING", codes(pod_phase="Pending"))
    def test_pending_pvc(self):
        self.assertIn("PVC_PENDING", codes(pvc_phase="Pending"))
    def test_dns_degraded(self):
        self.assertIn("DNS_OPERATOR_DEGRADED", codes(dns_operator="Degraded"))
    def test_selector_mismatch(self):
        self.assertIn("SELECTOR_MISMATCH", codes(service_selector_matches=False))
    def test_networkpolicy_presence_is_not_cause(self):
        self.assertIn("POLICY_REVIEW", codes(network_policy_present=True))
    def test_route_and_endpoints_need_verification(self):
        self.assertIn("INGRESS_PATH_UNVERIFIED", codes(route_present=True))
    def test_no_decisive_signal(self):
        self.assertEqual(codes(), ["NO_DECISIVE_SIGNAL"])
    def test_multiple_signals_not_collapsed(self):
        result = codes(ready_endpoints=0, ready_replicas=0,
                       pvc_phase="Pending", dns_operator="Degraded")
        self.assertTrue({"PVC_PENDING", "DNS_OPERATOR_DEGRADED",
                         "NO_READY_ENDPOINTS"}.issubset(result))
    def test_report_does_not_claim_root_cause(self):
        obj = report(parse_case(json.dumps(BASE)))
        self.assertEqual(obj["status"], "HYPOTHESES_ONLY")
        self.assertTrue(obj["not_a_root_cause_confirmation"])
    def test_negative_replicas_rejected(self):
        with self.assertRaises(ValueError):
            parse_case(json.dumps({**BASE, "ready_replicas": -1}))
    def test_boolean_cannot_be_replica_count(self):
        with self.assertRaises(ValueError):
            parse_case(json.dumps({**BASE, "desired_replicas": True}))
    def test_ready_greater_than_desired_rejected(self):
        with self.assertRaises(ValueError):
            parse_case(json.dumps({**BASE, "ready_replicas": 3}))
    def test_unknown_key_rejected(self):
        with self.assertRaises(ValueError):
            parse_case(json.dumps({**BASE, "token": "secret"}))
    def test_missing_key_rejected(self):
        d = dict(BASE); del d["pod_phase"]
        with self.assertRaises(ValueError):
            parse_case(json.dumps(d))
    def test_unknown_event_reason_rejected(self):
        with self.assertRaises(ValueError):
            parse_case(json.dumps({**BASE, "last_event_reason": "CUSTOM"}))
    def test_oversized_input_rejected(self):
        with self.assertRaises(ValueError):
            parse_case("X" * (MAX_BYTES+1))


if __name__ == "__main__":
    unittest.main()
