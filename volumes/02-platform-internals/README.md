# Volume 02 — Architecture interne d'OpenShift

**Édition 1.0 du manuscrit : 10 chapitres, 3 laboratoires et 1 étude d'architecture.**  
**Référence : OpenShift Container Platform 4.22 · Kubernetes 1.35.**  
**Limite : documentation et tests Python offline, sans exécution de changements control plane ni de PRA sur CRC.**

## Table des chapitres

1. [Du client oc au control plane](01-control-plane-request-path.md) — API, etcd, reconcilers et responsabilités.
2. [etcd : Raft, quorum et restauration](02-etcd-consistency-and-recovery.md) — principes de majorité et backup.
3. [Scheduler, controller-manager et Leases](03-scheduler-controller-manager.md) — filtres, placement, leader election et PDB.
4. [CVO, release images et mise à jour](04-cvo-release-upgrades-operators.md) — OSUS, runlevels et Conditions.
5. [RHCOS, Ignition et Machine Config Operator](05-rhcos-ignition-mco-day2.md) — machine config et rollouts.
6. [kubelet, CRI-O et lifecycle Pod](06-kubelet-crio-pod-lifecycle.md) — images, cgroups, probes et arrêt gracieux.
7. [Admission : RBAC, SCC, PSA et webhooks](07-admission-rbac-scc-psa-webhooks.md) — contrats et pannes d'admission.
8. [API extensions et CRD versionnées](08-crd-apiextensions-versioning-conversion.md) — storage/served, conversion et status.
9. [Haute disponibilité du control plane](09-control-plane-ha-certificates-failure.md) — LB, certificats, quorum, domains de panne.
10. [Diagnostic N3 et soutenance d'architecture](10-n3-observability-design-review.md) — preuves et revue de risques.

[Glossaire de l'architecture interne](GLOSSARY.md).

## Annexes : ateliers

- [V02-L01 — Inventaire read-only du control plane](../../labs/v02-01-control-plane-readonly.md) : procédure documentée, non exécutée.
- [V02-L02 — Modèle de quorum etcd offline](../../labs/v02-02-etcd-quorum-offline.md) : deux scénarios, Python, 16 tests.
- [V02-L03 — Filtrage scheduling offline](../../labs/v02-03-scheduling-offline.md) : placement théorique, Python, 20 tests.
- [V02-C01 — Architecture bancaire : HA et mises à jour](../../case-studies/v02-control-plane/01-architecture-review-ha-upgrade.md) : dossier et ADR fictifs.

## Réalisation et preuve

- Documentation de référence : **PUBLIC_VERIFIED**, textes rédigés depuis les concepts et documents officiels.
- Simulateur Python : **OFFLINE_TEST**, ne se connecte pas à etcd/Kubernetes.
- Runbook d'inventaire : **DOCUMENTED_NOT_RUN**.
- Dossier bancaire : **REFERENCE_ARCHITECTURE**, pas un projet déployé ni une preuve de HA.
- Un éventuel **RUNTIME_PROVEN** exige date/version/topologie/protocole/observations réelles, absentes de cette publication.

**Aucun backup/restore etcd, aucune interruption de nœud et aucune modification du MCO, CVO ou SCC n'ont été lancés.**

[Notes d'édition](../../docs/V02_RELEASE_NOTES.md) · [Sources officielles](../../docs/SOURCES.md).
