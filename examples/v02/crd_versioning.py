"""Offline structural exercise for CRD versions and ConversionReview contracts.

This code is NOT an admission server and NOT a production webhook.
It intentionally supports only two compatible fictional profiles.
No imports of networking, Kubernetes clients, subprocess, kubeconfigs or secrets.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys

GROUP = "platform.example.com"
KIND = "CapabilityProfile"
VERSIONS = {f"{GROUP}/v1alpha1", f"{GROUP}/v1beta1"}
KEYS = {"apiVersion", "kind", "metadata", "spec", "status"}


def _check(obj: object) -> dict:
    if not isinstance(obj, dict) or not set(obj).issubset(KEYS):
        raise ValueError("invalid object shape")
    if not {"apiVersion", "kind", "metadata", "spec"}.issubset(obj):
        raise ValueError("required fields missing")
    version = obj["apiVersion"]
    if version not in VERSIONS or obj["kind"] != KIND:
        raise ValueError("kind or API version unsupported")
    md = obj["metadata"]
    if not isinstance(md, dict):
        raise ValueError("metadata object required")
    for name in ("name", "namespace"):
        if not isinstance(md.get(name), str) or not md[name]:
            raise ValueError(f"metadata.{name} required")
    if "uid" in md and not isinstance(md["uid"], str):
        raise ValueError("metadata.uid must be string")
    spec = obj["spec"]
    field = "enabled" if version.endswith("v1alpha1") else "profile"
    if not isinstance(spec, dict) or not {field}.issubset(spec) or not set(spec).issubset({field, "retentionDays"}):
        raise ValueError("spec fields invalid; refusing lossy conversion")
    if field == "enabled" and type(spec[field]) is not bool:
        raise ValueError("enabled must be boolean")
    if field == "profile" and spec[field] not in ("standard", "disabled"):
        raise ValueError("only standard or disabled supported")
    if "retentionDays" in spec and (type(spec["retentionDays"]) is not int
                                   or not 1 <= spec["retentionDays"] <= 365):
        raise ValueError("retentionDays must be integer 1..365")
    if "status" in obj and not isinstance(obj["status"], dict):
        raise ValueError("status must be object")
    return obj


def convert(obj: dict, desired_api_version: str) -> dict:
    """Convert a single fixture; refuse unknown fields and unrepresentable states."""
    if desired_api_version not in VERSIONS:
        raise ValueError("unsupported target version")
    obj = _check(obj)
    result = deepcopy(obj)
    current = obj["apiVersion"]
    if current == desired_api_version:
        return result
    source = obj["spec"]
    if desired_api_version.endswith("v1beta1"):
        result["spec"] = {"profile": "standard" if source["enabled"] else "disabled"}
    else:
        result["spec"] = {"enabled": source["profile"] == "standard"}
    if "retentionDays" in source:
        result["spec"]["retentionDays"] = source["retentionDays"]
    result["apiVersion"] = desired_api_version
    return result


def review(request: dict) -> dict:
    """Produce successful ConversionReview v1 response or raise on invalid input.

    A real conversion webhook would also implement TLS, HTTP, authentication
    policy, limits, availability, metrics and the full Kubernetes protocol.
    """
    if not isinstance(request, dict) or set(request) != {"apiVersion", "kind", "request"}:
        raise ValueError("invalid ConversionReview envelope")
    if request["apiVersion"] != "apiextensions.k8s.io/v1" or request["kind"] != "ConversionReview":
        raise ValueError("unsupported ConversionReview")
    body = request["request"]
    if not isinstance(body, dict) or set(body) != {"uid", "desiredAPIVersion", "objects"}:
        raise ValueError("invalid request")
    uid, version, objects = body["uid"], body["desiredAPIVersion"], body["objects"]
    if not isinstance(uid, str) or not 1 <= len(uid) <= 128:
        raise ValueError("invalid review uid")
    if version not in VERSIONS:
        raise ValueError("unsupported target version")
    if not isinstance(objects, list) or len(objects) > 100:
        raise ValueError("conversion batch invalid")
    # Converted objects retain identity fields, ordering and status.
    converted = [convert(obj, version) for obj in objects]
    return {
        "apiVersion": "apiextensions.k8s.io/v1",
        "kind": "ConversionReview",
        "response": {
            "uid": uid,
            "result": {"status": "Success"},
            "convertedObjects": converted,
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m examples.v02.crd_versioning REVIEW.json", file=sys.stderr)
        return 2
    try:
        path = Path(argv[0])
        if path.stat().st_size > 16384:
            raise ValueError("offline input exceeds 16 KiB")
        output = review(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        print(f"invalid training fixture: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
