"""Offline *teaching* model for scheduler's hard filtering phase only.

Never calls Kubernetes, never binds a Pod. Inputs are fictitious integers:
CPU millicores, memory MiB. No priority/preemption, CSI, topology-spread,
full taint effect support, plugin scoring, or actual OCP support claim.

Usage:
python -m examples.v02.scheduling_filter examples/v02/cases/fit-and-taint.json
"""
from __future__ import annotations

import json
from pathlib import Path
import sys


MAX_BYTES = 16384
_NODE_KEYS = {
    "name", "zone", "labels", "taints",
    "cpu_allocatable_m", "cpu_requested_m",
    "memory_allocatable_mib", "memory_requested_mib",
}
_POD_KEYS = {"cpu_m", "memory_mib", "node_selector", "tolerations", "eligible_zones"}


def _positive_int(value: object, label: str, allow_zero: bool = False) -> int:
    if type(value) is not int or value < (0 if allow_zero else 1) or value > 10000000:
        raise ValueError(f"{label}: integer range invalid")
    return value


def validate_case(case: object) -> dict:
    """Structural validation of one offline scenario, without network or writes."""
    if not isinstance(case, dict) or set(case) != {"nodes", "pod"}:
        raise ValueError("expected exactly nodes and pod keys")
    nodes, pod = case["nodes"], case["pod"]
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 100:
        raise ValueError("nodes must be a nonempty list of at most 100 elements")
    if not isinstance(pod, dict) or set(pod) != _POD_KEYS:
        raise ValueError("pod keys missing/unknown")
    names: set[str] = set()
    for i, node in enumerate(nodes):
        if not isinstance(node, dict) or set(node) != _NODE_KEYS:
            raise ValueError(f"node[{i}] keys missing/unknown")
        if not isinstance(node["name"], str) or not (1 <= len(node["name"]) <= 80):
            raise ValueError("invalid node name")
        if not isinstance(node["zone"], str) or not (1 <= len(node["zone"]) <= 80):
            raise ValueError("invalid node zone")
        if node["name"] in names:
            raise ValueError("duplicate node name")
        names.add(node["name"])
        if not isinstance(node["labels"], dict) or any(
            not isinstance(k, str) or not isinstance(v, str)
            for k, v in node["labels"].items()
        ):
            raise ValueError("labels must be string dictionary")
        if not isinstance(node["taints"], list) or any(
            not isinstance(t, str) or not t or len(t) > 80
            for t in node["taints"]
        ):
            raise ValueError("taints must be simple training strings")
        for field in ("cpu_allocatable_m", "memory_allocatable_mib"):
            _positive_int(node[field], field)
        for requested, allocatable in (
            ("cpu_requested_m", "cpu_allocatable_m"),
            ("memory_requested_mib", "memory_allocatable_mib"),
        ):
            _positive_int(node[requested], requested, allow_zero=True)
            if node[requested] > node[allocatable]:
                raise ValueError(f"{requested} exceeds {allocatable}")
    _positive_int(pod["cpu_m"], "pod.cpu_m")
    _positive_int(pod["memory_mib"], "pod.memory_mib")
    if not isinstance(pod["node_selector"], dict) or any(
        not isinstance(k, str) or not isinstance(v, str)
        for k, v in pod["node_selector"].items()
    ):
        raise ValueError("node_selector must be string dictionary")
    for key in ("tolerations", "eligible_zones"):
        if not isinstance(pod[key], list) or any(
            not isinstance(v, str) or not v or len(v) > 80
            for v in pod[key]
        ):
            raise ValueError(f"{key} must be list of strings")
    return case


def assess(case: dict) -> dict:
    """Hard-filter illustration: NOT an implementation of kube-scheduler."""
    validate_case(case)
    pod = case["pod"]
    decisions = []
    for node in case["nodes"]:
        reasons = []
        if node["cpu_requested_m"] + pod["cpu_m"] > node["cpu_allocatable_m"]:
            reasons.append("Insufficient CPU requests capacity")
        if node["memory_requested_mib"] + pod["memory_mib"] > node["memory_allocatable_mib"]:
            reasons.append("Insufficient memory requests capacity")
        if any(node["labels"].get(k) != v for k, v in pod["node_selector"].items()):
            reasons.append("NodeSelectorMismatch")
        if any(taint not in pod["tolerations"] for taint in node["taints"]):
            reasons.append("UntoleratedTaint")
        if pod["eligible_zones"] and node["zone"] not in pod["eligible_zones"]:
            reasons.append("ZoneExcluded")
        decisions.append({
            "name": node["name"],
            "eligible": not reasons,
            "reasons": reasons,
        })
    return {
        "model": "OFFLINE_HARD_FILTER_ONLY",
        "not_a_real_scheduler": True,
        "eligible_nodes": [x["name"] for x in decisions if x["eligible"]],
        "decisions": decisions,
        "limitations": [
            "No Kubernetes API or scheduler framework interaction",
            "No CSI, hostports, topology skew, priority/preemption or scoring",
            "Taints represented as simple strings, not Kubernetes taint effects",
            "Successful hard filter does not imply a Pod will be bound or Ready",
        ],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m examples.v02.scheduling_filter CASE.json", file=sys.stderr)
        return 2
    try:
        source = Path(argv[0])
        if source.stat().st_size > MAX_BYTES:
            raise ValueError("oversized training scenario")
        obj = json.loads(source.read_text(encoding="utf-8"))
        result = assess(obj)
    except (ValueError, TypeError, OSError, UnicodeError) as err:
        print(f"invalid scenario: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
