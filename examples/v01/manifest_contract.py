"""Offline structural review of a deliberately NON-DEPLOYABLE OCP reference bundle.

Kubernetes JSON manifests are valid API input (JSON is compatible with YAML 1.2).
Not an API schema validator, not an SCC/PSA check, not a runtime security audit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent / "manifest-contract"
BUNDLE_NAMES = [
    "00-namespace.json", "01-serviceaccount.json", "02-deployment.json",
    "03-service.json", "04-route.json", "05-default-deny.json",
]


def load_bundle() -> list[dict[str, Any]]:
    return [json.loads((BASE / name).read_text(encoding="utf-8"))
            for name in BUNDLE_NAMES]


def validate_bundle(objects: list[dict[str, Any]]) -> list[str]:
    """Return actionable errors; no network, no file writes, no shell commands."""
    errors: list[str] = []
    expected = {"Namespace", "ServiceAccount", "Deployment", "Service",
                "Route", "NetworkPolicy"}
    by_kind: dict[str, dict[str, Any]] = {}
    for obj in objects:
        kind = obj.get("kind", "")
        if kind in by_kind:
            errors.append(f"duplicate kind in teaching bundle: {kind}")
        by_kind[kind] = obj
        if not obj.get("apiVersion"):
            errors.append(f"{kind}: apiVersion missing")
        if not obj.get("metadata", {}).get("name"):
            errors.append(f"{kind}: metadata.name missing")

    for kind in sorted(expected - by_kind.keys()):
        errors.append(f"required resource {kind} absent")
    if errors:
        return errors

    ns = by_kind["Namespace"]["metadata"]["name"]
    for kind, obj in by_kind.items():
        if kind == "Namespace":
            continue
        if obj.get("metadata", {}).get("namespace") != ns:
            errors.append(f"{kind}: unexpected namespace (expected {ns})")

    deploy = by_kind["Deployment"]
    template = deploy.get("spec", {}).get("template", {})
    podspec = template.get("spec", {})
    labels = template.get("metadata", {}).get("labels", {})
    selector = deploy.get("spec", {}).get("selector", {}).get("matchLabels", {})
    for k, v in selector.items():
        if labels.get(k) != v:
            errors.append(f"Deployment: pod label {k} does not match selector")
    if not selector:
        errors.append("Deployment: selector is empty")
    service = by_kind["Service"]
    svc_selectors = service.get("spec", {}).get("selector", {})
    if not svc_selectors or any(labels.get(k) != v for k, v in svc_selectors.items()):
        errors.append("Service: selector does not select Pod template")
    if service.get("spec", {}).get("type") != "ClusterIP":
        errors.append("Service: example must remain ClusterIP")

    sa_name = by_kind["ServiceAccount"]["metadata"]["name"]
    if podspec.get("serviceAccountName") != sa_name:
        errors.append("Deployment: incorrect ServiceAccount reference")
    if podspec.get("automountServiceAccountToken") is not False:
        errors.append("Deployment: API token auto-mount must be disabled")
    if by_kind["ServiceAccount"].get("automountServiceAccountToken") is not False:
        errors.append("ServiceAccount: API token auto-mount must be disabled")
    if podspec.get("hostNetwork") is True:
        errors.append("Deployment: hostNetwork forbidden by teaching contract")
    security = podspec.get("securityContext", {})
    if security.get("runAsNonRoot") is not True:
        errors.append("Deployment: runAsNonRoot required")
    if security.get("seccompProfile", {}).get("type") != "RuntimeDefault":
        errors.append("Deployment: RuntimeDefault seccomp required")

    containers = podspec.get("containers", [])
    if len(containers) != 1:
        errors.append("Deployment: expected exactly one teaching container")
        return errors
    container = containers[0]
    image = container.get("image", "")
    if not (image.startswith("registry.example.invalid/") and
            image.endswith("REPLACE_WITH_REAL_DIGEST_BEFORE_ANY_DEPLOYMENT")):
        errors.append("Deployment: keep deliberately invalid teaching image")
    cs = container.get("securityContext", {})
    if cs.get("allowPrivilegeEscalation") is not False:
        errors.append("Container: allowPrivilegeEscalation must be false")
    if cs.get("readOnlyRootFilesystem") is not True:
        errors.append("Container: readOnlyRootFilesystem must be true")
    if "ALL" not in cs.get("capabilities", {}).get("drop", []):
        errors.append("Container: capabilities must drop ALL")
    resources = container.get("resources", {})
    for bucket in ("requests", "limits"):
        for resource in ("cpu", "memory"):
            if not resources.get(bucket, {}).get(resource):
                errors.append(f"Container: {bucket}.{resource} missing")
    ports = {p.get("name"): p.get("containerPort")
             for p in container.get("ports", [])}
    if not ports.get("http"):
        errors.append("Container: named http port missing")

    for probe in ("livenessProbe", "readinessProbe"):
        target = container.get(probe, {}).get("httpGet", {}).get("port")
        if target not in ports:
            errors.append(f"Container: {probe} targets an unknown named port")

    ports_svc = service.get("spec", {}).get("ports", [])
    if len(ports_svc) != 1:
        errors.append("Service: expected one port")
    elif ports_svc[0].get("targetPort") not in ports:
        errors.append("Service: targetPort not defined by container")

    route = by_kind["Route"].get("spec", {})
    if route.get("to", {}).get("name") != service["metadata"]["name"]:
        errors.append("Route: target Service differs from bundle")
    if route.get("port", {}).get("targetPort") not in {
        p.get("name") for p in ports_svc
    }:
        errors.append("Route: targetPort not defined by Service")
    if route.get("tls", {}).get("termination") != "edge":
        errors.append("Route: teaching contract documents edge termination")
    if not route.get("host", "").endswith(".invalid"):
        errors.append("Route: training host must remain non-routable .invalid")

    policy = by_kind["NetworkPolicy"].get("spec", {})
    net_selector = policy.get("podSelector", {}).get("matchLabels", {})
    if not net_selector or any(labels.get(k) != v for k, v in net_selector.items()):
        errors.append("NetworkPolicy: must select same application Pods")
    if set(policy.get("policyTypes", [])) != {"Ingress", "Egress"}:
        errors.append("NetworkPolicy: must deny both ingress and egress")
    if policy.get("ingress") != [] or policy.get("egress") != []:
        errors.append("NetworkPolicy: reference must remain default-deny")

    return errors


if __name__ == "__main__":
    problems = validate_bundle(load_bundle())
    if problems:
        for problem in problems:
            print("FAIL:", problem)
        raise SystemExit(1)
    print(f"PASS: structural contract ({len(BUNDLE_NAMES)} non-deployable JSON objects)")
