# Volume 02 — Architecture interne d'OpenShift

**Édition documentaire 1.2 : couverture de contenu terminée pour 12 chapitres, 6 laboratoires, 1 étude d'architecture et 4 schémas SVG; aucune preuve runtime inventée.**  
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

[Télécharger le PDF 1.1 — 85 pages](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.1-20261011/OpenShift_Masterbook_Volume_02_Edition_1_1_Zidane_Djamal_2026.pdf) · [Validation du PDF](../../docs/V02_RELEASE_VERIFICATION_1_1.md) · [Notes d'édition](../../docs/V02_RELEASE_NOTES.md) · [Sources officielles](../../docs/SOURCES.md).

**Le PDF 1.1 publié reste un instantané historique de 10 chapitres ; les 2 nouveaux chapitres et le lab L04 ne figurent pas dans ce PDF. Le manuscrit Markdown à jour fait foi.**

**Le nombre de pages ne mesure pas la complétude.** Cette édition a une couverture technique substantielle, et ses écarts restants sont suivis par domaine dans la [grille de validation du contenu](../../docs/V02_CONTENT_ACCEPTANCE.md). Les autres figures Mermaid non converties restent dans la source Markdown et sous forme de texte lisible dans le PDF.

**QA actuelle :** [114 tests offline/éditoriaux et 111 liens locaux réussis](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38155313628). Les éléments de Machine API, OLM et conversion restent soumis à une revue technique de compatibilité et ne portent aucune preuve runtime.


## Prévisualisation du manuscrit actuel

L'édition PDF 1.1 reste la dernière release publique; elle ne contient pas les chapitres Machine API et OLM ajoutés ensuite. [Un PDF brouillon contenant les 12 chapitres et 6 ateliers a été construit et vérifié par GitHub Actions](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38156129697) (artefact téléchargeable depuis le run). Il est réservé à la relecture avant une nouvelle édition. Aucun quota de pages n'est utilisé pour décider de la clôture.


[Revue technique et décision de clôture documentaire](../../docs/V02_TECHNICAL_AUDIT_20261012.md) · [Avis au lecteur](../../docs/V02_1_2_READER_NOTICE.md). L'édition 1.2 remplace l'édition 1.1 comme référence documentaire dès publication vérifiée sur GitHub Releases; l'édition 1.1 reste archivée.