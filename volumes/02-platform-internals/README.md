# Volume 02 — Architecture interne d'OpenShift

**Édition documentaire 1.3 : couverture de contenu terminée pour 12 chapitres, 6 laboratoires, 1 étude d'architecture et 4 schémas SVG; aucune preuve runtime inventée.**  
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
11. [Machine API, MachineSets et autoscaling](11-machine-api-machinesets-autoscaling.md) — Machines, Nodes, MHC, autoscalers, frontières de support.
12. [OLM Classic et OLM v1](12-olm-classic-v1-extensions-lifecycle.md) — bundles, CSV, InstallPlan, ClusterCatalog et ClusterExtension.

[Glossaire de l'architecture interne](GLOSSARY.md).

## Annexes : ateliers

- [V02-L01 — Inventaire read-only du control plane](../../labs/v02-01-control-plane-readonly.md) : procédure documentée, non exécutée.
- [V02-L02 — Modèle de quorum etcd offline](../../labs/v02-02-etcd-quorum-offline.md) : deux scénarios, Python, 16 tests.
- [V02-L03 — Filtrage scheduling offline](../../labs/v02-03-scheduling-offline.md) : placement théorique, Python, 20 tests.
- [V02-L04 — Conversion CRD versionnée offline](../../labs/v02-04-crd-conversion-offline.md) : schémas alpha/beta, ConversionReview et 20 tests de compatibilité.
- [V02-L05 — Machine API et autoscaling](../../labs/v02-05-machine-api-capacity-paper.md) : calcul de capacité et chaîne de contrôleurs, exercice corrigé sur papier.
- [V02-L06 — OLM Classic versus OLM v1](../../labs/v02-06-olm-operator-lifecycle-paper.md) : choix du cycle de vie, sécurité d'upgrade et CRD, exercice corrigé sur papier.
- [V02-C01 — Architecture bancaire : HA et mises à jour](../../case-studies/v02-control-plane/01-architecture-review-ha-upgrade.md) : dossier et ADR fictifs.

## Réalisation et preuve

- Documentation de référence : **PUBLIC_VERIFIED**, textes rédigés depuis les concepts et documents officiels.
- Simulateur Python : **OFFLINE_TEST**, ne se connecte pas à etcd/Kubernetes.
- Runbook d'inventaire : **DOCUMENTED_NOT_RUN**.
- Dossier bancaire : **REFERENCE_ARCHITECTURE**, pas un projet déployé ni une preuve de HA.
- Un éventuel **RUNTIME_PROVEN** exige date/version/topologie/protocole/observations réelles, absentes de cette publication.

**Aucun backup/restore etcd, aucune interruption de nœud et aucune modification du MCO, CVO ou SCC n'ont été lancés.**

## Édition documentaire finale pour ce périmètre

- [PDF édition 1.3 — téléchargement](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.3-20261012/OpenShift_Masterbook_Volume_02_Edition_1_3_Zidane_Djamal_2026.pdf) · [Release GitHub](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.3-20261012)
- [Compte rendu de publication et contrôle visuel](../../docs/V02_RELEASE_VERIFICATION_1_3.md)
- [Audit technique et statut des preuves](../../docs/V02_TECHNICAL_AUDIT_20261012.md)
- [Erratum relatif à OCP 4.22](../../docs/ERRATA_V01_V02_20261011.md)
- [Sources et politique des droits](../../docs/RIGHTS_AND_LICENSING.md)

**CLOSED_DOCUMENTARY_SCOPE.** Le contenu prévu de l'architecture interne OCP 4.22 est couvert; ce statut ne prouve pas de tests runtime multinœuds, d'upgrade de cluster, de restore etcd ni de conversion CRD déployée. Les éditions 1.0, 1.1 et 1.2 restent archivées.
