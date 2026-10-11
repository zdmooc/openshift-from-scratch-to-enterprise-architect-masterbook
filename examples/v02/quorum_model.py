"""Pure offline majority/quorum model for teaching, never an etcd recovery tool.

Input: fictional voting member IDs and failure domains.
This does NOT assess disk, latency, Raft terms, storage integrity or OCP support.
Usage: python -m examples.v02.quorum_model examples/v02/cases/etcd-three-zones.json
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys


@dataclass(frozen=True)
class Member:
    id: str
    zone: str


def majority(voters: int) -> int:
    if type(voters) is not int or voters < 1 or voters > 100:
        raise ValueError("voting members must be integer 1..100")
    return voters // 2 + 1


def validate_case(data: dict) -> tuple[list[Member], set[str]]:
    if not isinstance(data, dict) or set(data) != {"members", "lost_zones"}:
        raise ValueError("expected members and lost_zones only")
    if not isinstance(data["members"], list) or not isinstance(data["lost_zones"], list):
        raise ValueError("lists required")
    if not (1 <= len(data["members"]) <= 100):
        raise ValueError("member count outside 1..100")
    if any(not isinstance(m, dict) or set(m) != {"id", "zone"}
           for m in data["members"]):
        raise ValueError("member requires id, zone")
    ids: list[str] = []
    for m in data["members"]:
        if not isinstance(m["id"], str) or not m["id"].strip():
            raise ValueError("member id must be a string")
        if not isinstance(m["zone"], str) or not m["zone"].strip():
            raise ValueError("zone must be a string")
        if len(m["id"]) > 80 or len(m["zone"]) > 80:
            raise ValueError("id/zone too long")
        ids.append(m["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate members")
    lost = data["lost_zones"]
    if any(not isinstance(z, str) or not z or len(z) > 80 for z in lost):
        raise ValueError("lost_zones must contain short strings")
    if len(lost) != len(set(lost)):
        raise ValueError("duplicate zones")
    existing = {m["zone"] for m in data["members"]}
    if not set(lost).issubset(existing):
        raise ValueError("unknown lost zone")
    return [Member(m["id"], m["zone"]) for m in data["members"]], set(lost)


def assess(data: dict) -> dict:
    members, lost = validate_case(data)
    present = [m for m in members if m.zone not in lost]
    absent = [m for m in members if m.zone in lost]
    count = len(members)
    threshold = majority(count)
    return {
        "model": "OFFLINE_QUORUM_COUNT_ONLY",
        "voters": count,
        "majority": threshold,
        "available_voters": len(present),
        "unavailable_voters": len(absent),
        "majority_possible": len(present) >= threshold,
        "lost_zones": sorted(lost),
        "not_runtime_proof": True,
        "warnings": [
            "No live etcd nodes checked",
            "Majority count does not ensure operational quorum/latency",
            "Do not infer OpenShift control-plane topology support",
        ],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m examples.v02.quorum_model CASE.json", file=sys.stderr)
        return 2
    file = Path(argv[0])
    try:
        if file.stat().st_size > 8192:
            raise ValueError("case exceeds size limit")
        data = json.loads(file.read_text(encoding="utf-8"))
        result = assess(data)
    except (OSError, UnicodeError, ValueError, TypeError) as err:
        print(f"Invalid offline case: {err}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
