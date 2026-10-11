"""CRD version conversion — 20 offline tests, not API-server integration."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from examples.v02.crd_versioning import convert, review

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples/v02/crd-versioning"
ALPHA = json.loads((FIXTURES / "alpha.json").read_text(encoding="utf-8"))
BETA = json.loads((FIXTURES / "beta.json").read_text(encoding="utf-8"))
REVIEW = json.loads((FIXTURES / "review.json").read_text(encoding="utf-8"))
V1A = "platform.example.com/v1alpha1"
V1B = "platform.example.com/v1beta1"


class CRDVersioningTests(unittest.TestCase):
    def test_legacy_to_beta(self):
        self.assertEqual(convert(ALPHA, V1B)["spec"], BETA["spec"])

    def test_beta_to_legacy(self):
        self.assertEqual(convert(BETA, V1A)["spec"], ALPHA["spec"])

    def test_round_trip_preserves_content(self):
        self.assertEqual(convert(convert(ALPHA, V1B), V1A), ALPHA)

    def test_unchanged_version_returns_copy(self):
        self.assertEqual(convert(ALPHA, V1A), ALPHA)
        self.assertIsNot(convert(ALPHA, V1A), ALPHA)

    def test_metadata_never_mutated(self):
        self.assertEqual(convert(ALPHA, V1B)["metadata"], ALPHA["metadata"])

    def test_status_preserved(self):
        self.assertEqual(convert(ALPHA, V1B)["status"], ALPHA["status"])

    def test_disabled_round_trip(self):
        item = deepcopy(ALPHA)
        item["spec"]["enabled"] = False
        self.assertEqual(convert(item, V1B)["spec"]["profile"], "disabled")
        self.assertEqual(convert(convert(item, V1B), V1A), item)

    def test_optional_retention_absent(self):
        item = deepcopy(ALPHA)
        del item["spec"]["retentionDays"]
        self.assertNotIn("retentionDays", convert(item, V1B)["spec"])

    def test_unknown_spec_rejected_not_discarded(self):
        item = deepcopy(ALPHA)
        item["spec"]["privileged"] = True
        with self.assertRaises(ValueError):
            convert(item, V1B)

    def test_unknown_profile_rejected(self):
        item = deepcopy(BETA)
        item["spec"]["profile"] = "enhanced"
        with self.assertRaises(ValueError):
            convert(item, V1A)

    def test_wrong_boolean_type_rejected(self):
        item = deepcopy(ALPHA)
        item["spec"]["enabled"] = 1
        with self.assertRaises(ValueError):
            convert(item, V1B)

    def test_retention_out_of_range_rejected(self):
        item = deepcopy(ALPHA)
        item["spec"]["retentionDays"] = 366
        with self.assertRaises(ValueError):
            convert(item, V1B)

    def test_unknown_api_version_rejected(self):
        with self.assertRaises(ValueError):
            convert(ALPHA, "platform.example.com/v2")

    def test_wrong_kind_rejected(self):
        item = deepcopy(ALPHA)
        item["kind"] = "Secret"
        with self.assertRaises(ValueError):
            convert(item, V1B)

    def test_namespace_required(self):
        item = deepcopy(ALPHA)
        del item["metadata"]["namespace"]
        with self.assertRaises(ValueError):
            convert(item, V1B)

    def test_conversion_review_contract(self):
        out = review(REVIEW)
        self.assertEqual(out["response"]["uid"], REVIEW["request"]["uid"])
        self.assertEqual(out["response"]["result"]["status"], "Success")
        self.assertEqual(out["response"]["convertedObjects"][0]["apiVersion"], V1B)

    def test_review_does_not_mutate_input(self):
        req = deepcopy(REVIEW)
        review(req)
        self.assertEqual(req, REVIEW)

    def test_review_batch_order(self):
        req = deepcopy(REVIEW)
        second = deepcopy(ALPHA)
        second["metadata"]["name"] = "secondary"
        req["request"]["objects"].append(second)
        objs = review(req)["response"]["convertedObjects"]
        self.assertEqual([x["metadata"]["name"] for x in objs], ["payments-api", "secondary"])

    def test_review_unknown_field_rejected(self):
        req = deepcopy(REVIEW)
        req["request"]["token"] = "do-not-process"
        with self.assertRaises(ValueError):
            review(req)

    def test_crd_has_two_versions_and_webhook(self):
        data = json.loads((FIXTURES / "crd-example-not-deployable.json").read_text(encoding="utf-8"))
        self.assertEqual(data["kind"], "CustomResourceDefinition")
        versions = data["spec"]["versions"]
        self.assertEqual(len(versions), 2)
        self.assertEqual(sum(v["storage"] for v in versions), 1)
        self.assertTrue(all(v["served"] for v in versions))
        self.assertEqual(data["spec"]["conversion"]["strategy"], "Webhook")
        self.assertEqual(data["spec"]["conversion"]["webhook"]["conversionReviewVersions"], ["v1"])


if __name__ == "__main__":
    unittest.main()
