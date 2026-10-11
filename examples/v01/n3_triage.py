"""Offline, evidence-preserving incident triage for OpenShift training.

No oc, network, subprocess, kubeconfig or writes. Avoid real production payloads.
Signals are sanitized and fictional. Output: hypotheses to VERIFY, not root cause.
Run: python -m examples.v01.n3_triage examples/v01/incident-cases/no-endpoints.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED = {
    "case_id", "service", "desired_replicas", "ready_replicas", "ready_endpoints",
    "pod_phase", "last_event_reason", "pvc_phase", "dns_operator",
    "route_present", "service_selector_matches", "network_policy_present",
}
ENUMS = {
    "pod_phase": {"Running", "Pending", "Failed", "Unknown", "NotObserved"},
    "pvc_phase": {"Bound", "Pending", "Lost", "NotApplicable", "NotObserved"},
    "dns_operator": {"Available", "Degraded", "Unknown"},
}
REASONS = {
    "ReadinessProbeFailed", "FailedScheduling", "FailedMount",
    "ImagePullBackOff", "OOMKilled", "None", "Unknown",
}
MAX_BYTES = 8192


@dataclass(frozen=True)
class Finding:
    code: str
    confidence: str
    evidence: str
    next_check: str


def parse_case(text: str) -> dict[str, Any]:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("training case exceeds 8192 bytes")
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise ValueError("case must be an object")
    unknown = set(obj) - ALLOWED
    if unknown:
        raise ValueError("unexpected keys: " + ",".join(sorted(unknown)))
    required = {"case_id", "service", "desired_replicas", "ready_replicas",
                "ready_endpoints", "pod_phase", "last_event_reason",
                "pvc_phase", "dns_operator", "route_present",
                "service_selector_matches", "network_policy_present"}
    if set(obj) != required:
        raise ValueError("missing keys: " + ",".join(sorted(required-set(obj))))
    for field in ("case_id", "service"):
        if not isinstance(obj[field], str) or not 1 <= len(obj[field]) <= 72:
            raise ValueError(f"{field} must be a short nonempty string")
    for field in ("desired_replicas", "ready_replicas", "ready_endpoints"):
        if type(obj[field]) is not int or not 0 <= obj[field] <= 10000:
            raise ValueError(f"{field} must be a nonnegative integer")
    if obj["ready_replicas"] > obj["desired_replicas"]:
        raise ValueError("ready_replicas exceeds desired_replicas")
    for field, allowed in ENUMS.items():
        if obj[field] not in allowed:
            raise ValueError(f"unsupported {field}")
    if obj["last_event_reason"] not in REASONS:
        raise ValueError("unsupported event reason")
    for field in ("route_present", "service_selector_matches",
                  "network_policy_present"):
        if type(obj[field]) is not bool:
            raise ValueError(f"{field} must be boolean")
    return obj


def diagnose(case: dict[str, Any]) -> list[Finding]:
    # Explicitly independent rules; results are leads, not causal certainty.
    findings: list[Finding] = []
    if not case["service_selector_matches"]:
        findings.append(Finding(
            "SELECTOR_MISMATCH", "high", "Service selector differs from Pod labels",
            "Read Service selector, Pod template labels, and EndpointSlices"))
    if case["ready_endpoints"] == 0:
        findings.append(Finding(
            "NO_READY_ENDPOINTS", "high", "0 ready EndpointSlice backends",
            "Verify readiness, Service selector, Pod ports and EndpointSlices"))
    if case["ready_replicas"] < case["desired_replicas"]:
        findings.append(Finding(
            "REPLICAS_UNAVAILABLE", "medium", "ready replicas less than desired",
            "Inspect Deployment conditions, Pods and Events"))
    if case["pod_phase"] == "Pending":
        findings.append(Finding(
            "POD_PENDING", "medium", "a Pod is Pending",
            "Inspect scheduler events, taints, requests, quotas and volume topology"))
    if case["pvc_phase"] == "Pending":
        findings.append(Finding(
            "PVC_PENDING", "medium", "a PVC is Pending",
            "Inspect StorageClass bindingMode, CSI driver and PVC events"))
    if case["dns_operator"] == "Degraded":
        findings.append(Finding(
            "DNS_OPERATOR_DEGRADED", "medium", "DNS Operator marked Degraded",
            "Check DNS Operator conditions and actual resolution failures"))
    if case["last_event_reason"] not in {"None", "Unknown"}:
        findings.append(Finding(
            "POD_EVENT", "medium", "event reason: " + case["last_event_reason"],
            "Check timestamped, sanitized Pod events and controller conditions"))
    if case["route_present"] and case["ready_endpoints"] > 0:
        findings.append(Finding(
            "INGRESS_PATH_UNVERIFIED", "low", "Route exists and ready endpoints exist",
            "Confirm TLS mode, router source, NetworkPolicy and app SLI"))
    if case["network_policy_present"]:
        findings.append(Finding(
            "POLICY_REVIEW", "low", "namespace contains NetworkPolicy resources",
            "Determine selected Pods and actual ingress/egress rules"))
    if not findings:
        findings.append(Finding(
            "NO_DECISIVE_SIGNAL", "low", "input lacks discriminating failure signals",
            "Gather service latency/errors, dependencies, rollout history and logs"))
    return findings


def report(case: dict[str, Any]) -> dict[str, Any]:
    findings = diagnose(case)
    return {
        "case_id": case["case_id"],
        "service": case["service"],
        "status": "HYPOTHESES_ONLY",
        "not_a_root_cause_confirmation": True,
        "findings": [f.__dict__ for f in findings],
    }


def main(args: list[str]) -> int:
    if len(args) != 1:
        print("usage: python -m examples.v01.n3_triage CASE.json", file=sys.stderr)
        return 2
    try:
        path = Path(args[0])
        if not path.is_file():
            raise ValueError("case path must point to an existing file")
        if path.stat().st_size > MAX_BYTES:
            raise ValueError("case too large")
        data = parse_case(path.read_text(encoding="utf-8"))
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"invalid case: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report(data), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
