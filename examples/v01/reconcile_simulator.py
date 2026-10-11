"""Simulate one Kubernetes-style reconciliation contract, without Kubernetes.

Teaching model only: no API server, cache, RBAC, SSA, networking or containers.
Execute: python -m unittest discover -s tests -v
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Desired:
    name: str = "payments-api"
    replicas: int = 2
    image: str = "registry.invalid/payments-api@sha256:ILLUSTRATIVE_ONLY"
    generation: int = 1
    deleting: bool = False
    deletion_policy: str = "Retain"


@dataclass
class Resource:
    kind: str
    spec: dict[str, object]
    owner: str
    annotations: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Status:
    ready: bool
    progressing: bool
    degraded: bool
    reason: str
    observed_generation: int


class TransientError(RuntimeError):
    """A simulated one-time failure of an API operation."""


class SimulatedAPI:
    """An in-memory store that records writes, not an API server emulator."""

    def __init__(self) -> None:
        self.resources: dict[str, Resource] = {}
        self.writes: list[tuple[str, str]] = []
        self.fail_next_for: set[str] = set()
        self.ready_replicas: int = 0

    def fail_once(self, key: str) -> None:
        self.fail_next_for.add(key)

    def apply_owned(self, key: str, spec: dict[str, object], owner: str) -> None:
        if key in self.fail_next_for:
            self.fail_next_for.remove(key)
            raise TransientError(f"API unavailable while applying {key}")
        current = self.resources.get(key)
        if current is not None and current.owner != owner:
            raise PermissionError(f"{key} is not owned by {owner}")
        if current is None:
            self.resources[key] = Resource(kind=key.split("/", 1)[0],
                                           spec=dict(spec), owner=owner)
            self.writes.append(("create", key))
        elif current.spec != spec:
            current.spec = dict(spec)
            # Annotations owned by another actor are intentionally untouched.
            self.writes.append(("update", key))

    def delete_owned(self, key: str, owner: str) -> None:
        item = self.resources.get(key)
        if item is None:
            return  # An already completed operation is safe to repeat.
        if item.owner != owner:
            raise PermissionError(f"refusing to delete non-owned {key}")
        del self.resources[key]
        self.writes.append(("delete", key))


class PaymentOperator:
    """A minimal, synchronous, deterministic reconcile algorithm."""

    OWNER = "v01-training-operator"

    def __init__(self, api: SimulatedAPI):
        self.api = api

    def reconcile(self, desired: Desired) -> Status:
        if not desired.name or desired.replicas < 0 or desired.replicas > 10:
            return Status(False, False, True, "InvalidSpec", desired.generation)
        if not desired.image.strip():
            return Status(False, False, True, "MissingImage", desired.generation)
        if desired.deletion_policy not in {"Retain", "Delete"}:
            return Status(False, False, True, "InvalidDeletionPolicy",
                          desired.generation)

        deployment = f"deployment/{desired.name}"
        service = f"service/{desired.name}"
        if desired.deleting:
            if desired.deletion_policy == "Delete":
                try:
                    self.api.delete_owned(service, self.OWNER)
                    self.api.delete_owned(deployment, self.OWNER)
                except PermissionError:
                    return Status(False, False, True, "DeletionBlocked",
                                  desired.generation)
                return Status(False, False, False, "Deleted", desired.generation)
            return Status(False, False, False, "Retained", desired.generation)

        try:
            self.api.apply_owned(
                deployment,
                {"replicas": desired.replicas, "image": desired.image},
                self.OWNER,
            )
            self.api.apply_owned(
                service,
                {"port": 8080, "selector": {"app": desired.name}},
                self.OWNER,
            )
        except (TransientError, PermissionError):
            # The first operation may have succeeded: next reconcile
            # must recover without creating a duplicate resource.
            return Status(False, False, True, "ReconcileFailed",
                          desired.generation)

        if self.api.ready_replicas >= desired.replicas:
            return Status(True, False, False, "Ready", desired.generation)
        return Status(False, True, False, "WaitingForReplicas",
                      desired.generation)


def demo() -> None:
    api = SimulatedAPI()
    operator = PaymentOperator(api)
    desired = Desired()
    print("first:", operator.reconcile(desired), "writes:", api.writes)
    print("repeat:", operator.reconcile(desired), "writes:", api.writes)
    api.ready_replicas = 2
    print("ready:", operator.reconcile(desired), "writes:", api.writes)


if __name__ == "__main__":
    demo()
