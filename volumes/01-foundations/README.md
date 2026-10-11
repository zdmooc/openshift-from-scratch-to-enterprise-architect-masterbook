# Volume 01 — Linux, Kubernetes et OpenShift

**Édition 1.0 : 13 chapitres éditorialement complets, 8 labs, 3 études d'architecture.**  
**Périmètre :** bases Linux, OCI, Kubernetes, OpenShift 4.22 et pratiques de diagnostic et d'architecture.

## Chapitres

1. [Pourquoi OpenShift ?](01-what-is-openshift.md)
2. [Desired state, reconciliation et Operators](02-desired-state-and-operators.md)
3. [Linux : namespaces, cgroups, isolation](03-linux-namespaces-cgroups.md)
4. [OCI, images, registries et runtimes](04-oci-images-runtimes.md)
5. [Kubernetes : API, scheduling et workloads](05-kubernetes-api-workloads.md)
6. [OpenShift : RHCOS, Operators, SCC et gouvernance](06-openshift-enterprise-primitives.md)
7. [Évaluation technique et soutenance](07-review-and-evaluation.md)
8. [Admission SCC/PSA, Routes TLS et NetworkPolicy](08-security-admission-routes.md)
9. [Réseau DNS, Services, TLS et diagnostic N3](09-network-dns-tls.md)
10. [Stockage : PV/PVC, CSI, StatefulSets et restore](10-storage-pv-pvc-csi.md)
11. [Méthodologie de diagnostic N3](11-n3-evidence-based-troubleshooting.md)
12. [ConfigMaps, Secrets, RBAC et multi-tenancy](12-config-secrets-tenancy.md)
13. [SRE, SLI/SLO, résilience et dimensionnement](13-reliability-slo-capacity.md)

[Glossaire](GLOSSARY.md)

## Laboratoires inclus comme annexes dans le PDF

- [L01 : observation OpenShift](../../labs/01-cluster-read-only.md) — lecture seule, non exécutée à cette publication.
- [L02 : namespaces/cgroups Linux](../../labs/02-linux-cgroup-readonly.md) — procédure documentée.
- [L03 : inspection OCI](../../labs/03-oci-image-readonly.md) — procédure documentée.
- [L04 : diagnostic API Kubernetes](../../labs/04-kubernetes-api-triage-readonly.md) — procédure documentée.
- [L05 : revue d'architecture bancaire](../../labs/05-architecture-review-payments.md) — paper lab.
- [L06 : simulateur de réconciliation](../../labs/06-controller-offline.md) — 10 tests Python hors cluster.
- [L07 : contrat de manifests OpenShift](../../labs/07-openshift-manifest-contract.md) — 14 tests Python hors cluster.
- [L08 : triage incident N3](../../labs/08-offline-n3-triage.md) — 18 tests Python hors cluster.

## Trois cas d'architecture

- [API bancaire : solution cible](../../case-studies/v01-banking-api/01-reference-architecture.md)
- [Runbook d'incident N3](../../case-studies/v01-banking-api/02-n3-triage-and-evidence.md)
- [ADR et modèle de dimensionnement](../../case-studies/v01-banking-api/03-adr-and-sizing.md)

## Édition et statut

La rédaction est terminée **pour le périmètre de la première édition**. L'absence de tests HA/DR en production ou sur cluster multi-nœuds reste explicitement déclarée. Les preuves offline ne sont pas des preuves Kubernetes runtime. Le PDF est construit de manière reproductible par [ce script](../../scripts/build_volume01_pdf.py), sans recours au CRC.

[Statuts de validation](../../docs/V01_PROGRESS.md) · [Notes de version](../../docs/V01_RELEASE_NOTES.md) · [Droits et licences](../../docs/RIGHTS_AND_LICENSING.md).
