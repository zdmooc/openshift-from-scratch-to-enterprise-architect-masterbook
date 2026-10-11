"""Offline deterministic checks for the training reconciler (not CRC tests)."""
import unittest

from examples.v01.reconcile_simulator import (
    Desired, PaymentOperator, Resource, SimulatedAPI,
)


class ReconcileContractTests(unittest.TestCase):
    def setUp(self):
        self.api = SimulatedAPI()
        self.operator = PaymentOperator(self.api)
        self.cr = Desired()

    def test_first_reconcile_creates_two_resources_then_waits(self):
        result = self.operator.reconcile(self.cr)
        self.assertTrue(result.progressing)
        self.assertFalse(result.ready)
        self.assertFalse(result.degraded)
        self.assertEqual(
            self.api.writes,
            [("create", "deployment/payments-api"), ("create", "service/payments-api")],
        )

    def test_second_reconcile_without_changes_does_not_write(self):
        self.operator.reconcile(self.cr)
        before = list(self.api.writes)
        second = self.operator.reconcile(self.cr)
        self.assertEqual(before, self.api.writes)
        self.assertEqual(second.reason, "WaitingForReplicas")

    def test_partial_failure_then_retry_is_idempotent(self):
        self.api.fail_once("service/payments-api")
        first = self.operator.reconcile(self.cr)
        self.assertTrue(first.degraded)
        self.assertIn("deployment/payments-api", self.api.resources)
        self.assertNotIn("service/payments-api", self.api.resources)
        second = self.operator.reconcile(self.cr)
        self.assertFalse(second.degraded)
        self.assertEqual(self.api.writes.count(("create", "deployment/payments-api")), 1)
        self.assertEqual(self.api.writes.count(("create", "service/payments-api")), 1)

    def test_drift_of_owned_spec_is_corrected_but_third_party_annotation_retained(self):
        self.operator.reconcile(self.cr)
        item = self.api.resources["deployment/payments-api"]
        item.spec["image"] = "unauthorized:latest"
        item.annotations["monitoring.example/team"] = "platform-sre"
        status = self.operator.reconcile(self.cr)
        self.assertFalse(status.degraded)
        self.assertEqual(item.spec["image"], self.cr.image)
        self.assertEqual(item.annotations["monitoring.example/team"], "platform-sre")
        self.assertIn(("update", "deployment/payments-api"), self.api.writes)

    def test_readiness_requires_observed_ready_replicas(self):
        self.operator.reconcile(self.cr)
        self.api.ready_replicas = 1
        self.assertFalse(self.operator.reconcile(self.cr).ready)
        self.api.ready_replicas = 2
        ready = self.operator.reconcile(self.cr)
        self.assertTrue(ready.ready)
        self.assertEqual(ready.observed_generation, 1)

    def test_invalid_spec_does_not_create_children(self):
        result = self.operator.reconcile(Desired(replicas=-3))
        self.assertTrue(result.degraded)
        self.assertEqual(result.reason, "InvalidSpec")
        self.assertEqual(self.api.writes, [])

    def test_delete_removes_only_owned_resources(self):
        self.operator.reconcile(self.cr)
        result = self.operator.reconcile(Desired(deleting=True, deletion_policy="Delete"))
        self.assertEqual(result.reason, "Deleted")
        self.assertEqual(self.api.resources, {})
        self.assertEqual(self.operator.reconcile(
            Desired(deleting=True, deletion_policy="Delete")).reason, "Deleted")
        self.assertEqual(self.api.writes.count(("delete", "deployment/payments-api")), 1)

    def test_retain_policy_keeps_resources(self):
        self.operator.reconcile(self.cr)
        result = self.operator.reconcile(Desired(deleting=True, deletion_policy="Retain"))
        self.assertEqual(result.reason, "Retained")
        self.assertEqual(len(self.api.resources), 2)
        self.assertEqual(len(self.api.writes), 2)

    def test_unowned_resource_is_not_overwritten(self):
        self.api.resources["deployment/payments-api"] = Resource(
            kind="deployment", spec={"replicas": 99},
            owner="another-operator",
        )
        result = self.operator.reconcile(self.cr)
        self.assertTrue(result.degraded)
        self.assertEqual(result.reason, "ReconcileFailed")
        self.assertEqual(self.api.resources["deployment/payments-api"].spec["replicas"], 99)

    def test_generation_is_reported_in_status(self):
        desired = Desired(generation=7, replicas=3)
        result = self.operator.reconcile(desired)
        self.assertEqual(result.observed_generation, 7)
        self.assertFalse(result.ready)


if __name__ == "__main__":
    unittest.main()
