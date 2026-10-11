"""Regression tests for static OpenShift manifest contracts.

No Kubernetes API or cluster is involved. Negative tests prove local checks
reject common drift/misconfiguration of the teaching artifact.
"""
import copy
import unittest

from examples.v01.manifest_contract import load_bundle, validate_bundle


class ManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.bundle = load_bundle()

    def change(self, kind, callback):
        copy_bundle = copy.deepcopy(self.bundle)
        for obj in copy_bundle:
            if obj["kind"] == kind:
                callback(obj)
                break
        return validate_bundle(copy_bundle)

    def test_baseline_valid(self):
        self.assertEqual(validate_bundle(self.bundle), [])

    def test_bad_service_selector_detected(self):
        errors = self.change("Service", lambda x: x["spec"]["selector"].update(
            {"app.kubernetes.io/name": "wrong"}))
        self.assertTrue(any("selector" in e for e in errors))

    def test_no_serviceaccount_token(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"].update(
            automountServiceAccountToken=True))
        self.assertTrue(any("auto-mount" in e for e in errors))

    def test_nonroot_enforced(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["securityContext"].update(
            runAsNonRoot=False))
        self.assertTrue(any("runAsNonRoot" in e for e in errors))

    def test_seccomp_enforced(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["securityContext"]["seccompProfile"].update(
            type="Unconfined"))
        self.assertTrue(any("seccomp" in e for e in errors))

    def test_no_privilege_escalation(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["containers"][0]["securityContext"].update(
            allowPrivilegeEscalation=True))
        self.assertTrue(any("allowPrivilegeEscalation" in e for e in errors))

    def test_capabilities_drop_all(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["containers"][0]["securityContext"]["capabilities"].update(
            drop=[]))
        self.assertTrue(any("drop ALL" in e for e in errors))

    def test_memory_limit_required(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"].pop(
            "memory"))
        self.assertTrue(any("limits.memory" in e for e in errors))

    def test_route_service_must_match(self):
        errors = self.change("Route", lambda x: x["spec"]["to"].update(name="wrong"))
        self.assertTrue(any("target Service" in e for e in errors))

    def test_route_tls_edge_enforced(self):
        errors = self.change("Route", lambda x: x["spec"]["tls"].update(termination="passthrough"))
        self.assertTrue(any("edge termination" in e for e in errors))

    def test_policy_cannot_silently_open_egress(self):
        errors = self.change("NetworkPolicy", lambda x: x["spec"].update(
            egress=[{"to": [{}]}]))
        self.assertTrue(any("default-deny" in e for e in errors))

    def test_route_host_must_not_be_routable(self):
        errors = self.change("Route", lambda x: x["spec"].update(host="payments.company.com"))
        self.assertTrue(any(".invalid" in e for e in errors))

    def test_namespace_isolation(self):
        errors = self.change("Service", lambda x: x["metadata"].update(
            namespace="production"))
        self.assertTrue(any("unexpected namespace" in e for e in errors))

    def test_image_placeholder_prevents_false_production_claim(self):
        errors = self.change("Deployment", lambda x: x["spec"]["template"]["spec"]["containers"][0].update(
            image="quay.io/example/app:latest"))
        self.assertTrue(any("teaching image" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
