# OpenShift — From Scratch to Enterprise Architect Masterbook

> **An independent, evidence-driven OpenShift & Kubernetes architecture reference**  
> Auteur : **Zidane Djamal** · Édition de travail : 2026–2030 · Langue principale : français

## Vision

Construire une référence pédagogique et opérationnelle qui relie les fondements Linux/containers/Kubernetes à l'architecture OpenShift d'entreprise, à l'exploitation Day-2 et aux dossiers d'architecture. **Ce projet n'est pas une publication officielle Red Hat.**

Les exemples pratiques, décisions d'architecture et procédures de vérification doivent être **originaux, traçables, versionnés et reproductibles**. Les preuves issues d'environnements de laboratoire ne sont jamais présentées comme des validations de production.

## Les 12 volumes

| # | Volume | Sujet |
|---|---|---|
| 01 | Foundations | Linux, OCI, containers, Kubernetes, introduction à OpenShift |
| 02 | Platform Internals | API, control plane, etcd, RHCOS, Operators, CVO/MCO |
| 03 | Install & Operate | CRC, SNO, IPI/UPI, bare metal, disconnected, day-1 |
| 04 | Networking | OVN-Kubernetes, DNS, Ingress, Routes, NetworkPolicy |
| 05 | Data & Storage | CSI, PV/PVC, ODF, StatefulSets, sauvegarde |
| 06 | Security & Compliance | RBAC, SCC, identity, secrets, policies, conformité |
| 07 | DevSecOps & GitOps | Pipelines, Helm, Kustomize, Argo CD, supply chain |
| 08 | Kubernetes Operators | Go, Kubebuilder, CRD, reconciliation, OLM, Day-2 |
| 09 | SRE & Troubleshooting | Prometheus, alerting, logs, capacity, incident N3 |
| 10 | HA, DR & Multicluster | Résilience, restore, upgrades, migration, gouvernance |
| 11 | Platform Engineering | IDP, Backstage, self-service, FinOps, Green IT |
| 12 | Advanced Architectures | RHOAI, virtualisation, EDA, banque/assurance, edge |

**Principe éditorial : seul le contenu compte.** Nombre de pages, de mots et de chapitres sont informatifs. Un volume est terminé quand les thèmes prévus sont correctement traités, expliqués et vérifiés, pas quand il atteint une pagination. Voir [la grille qualité](docs/EDITORIAL_STANDARD.md) et le [suivi de fond du Volume 02](docs/V02_CONTENT_ACCEPTANCE.md).

## Point de départ

1. [Cadrage maître](docs/MASTERBOOK_CHARTER.md)
2. [Sommaire éditorial](docs/VOLUME_MAP.md)
3. [Roadmap des itérations](docs/ROADMAP.md)
4. [Méthode de rédaction et de validation](docs/EDITORIAL_STANDARD.md)
5. [Matrice des preuves et des dépôts](docs/EVIDENCE_CATALOG.md)
6. [Politique de propriété intellectuelle](docs/RIGHTS_AND_LICENSING.md)
7. [Sources officielles et veille](docs/SOURCES.md)
8. [Volume 01 — Édition de contenu 1.0, 13 chapitres et glossaire](volumes/01-foundations/README.md)
9. [État réel du Volume 01 et travaux restant à valider](docs/V01_PROGRESS.md)
10. [Étude de cas : architecture API bancaire](case-studies/v01-banking-api/01-reference-architecture.md)
11. [Simulateur de réconciliation Python et tests](labs/06-controller-offline.md)
12. [Admission SCC/PSA, Routes TLS et NetworkPolicy](volumes/01-foundations/08-security-admission-routes.md)
13. [Atelier de validation de manifests OpenShift](labs/07-openshift-manifest-contract.md)
14. [Réseau : DNS, TLS et diagnostic](volumes/01-foundations/09-network-dns-tls.md)
15. [Stockage : PV/PVC, CSI, snapshots](volumes/01-foundations/10-storage-pv-pvc-csi.md)
16. [Méthode N3 et triage offline](volumes/01-foundations/11-n3-evidence-based-troubleshooting.md)
17. [Configuration et multi-tenancy](volumes/01-foundations/12-config-secrets-tenancy.md)
18. [SLO, fiabilité et dimensionnement](volumes/01-foundations/13-reliability-slo-capacity.md)
19. [Notes de l'édition PDF du Volume 01](docs/V01_RELEASE_NOTES.md)

## Règles fondamentales

- **Version explicite** pour chaque assertion sensible à une version OpenShift.
- **Aucune confusion** entre documentation de référence, démonstration locale et preuve de production.
- **Aucun changement destructif** d'un cluster dans les labs sans validation explicite.
- **Aucune copie non autorisée** de textes, illustrations ou dépôts tiers.
- **Publication PDF/EPUB** seulement après revue du contenu, des droits et des exercices.
- **Aucune licence générale présumée** avant inventaire des droits sur les contributions et contenus tiers.

## Marques et indépendance

OpenShift, Red Hat et les marques associées appartiennent à leurs titulaires respectifs. Ce projet est indépendant, sans affiliation ni approbation implicite de Red Hat.

© 2026 Zidane Djamal pour les contributions originales, sous réserve des droits des tiers. Voir [RIGHTS_AND_LICENSING.md](docs/RIGHTS_AND_LICENSING.md).


## Éditions publiées et travaux en cours

- **[Volume 01 — PDF édition 1.0](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v01.0-20261011)** : fondations (13 chapitres, 8 labs et cas bancaires).
- **[Volume 02 — PDF édition documentaire 1.3](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.3-20261012/OpenShift_Masterbook_Volume_02_Edition_1_3_Zidane_Djamal_2026.pdf)** : 12 chapitres, 6 labs, 1 étude bancaire, glossaire, avertissements et erratum. [Release immuable](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.3-20261012) · [validation CI réussie](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38217687784) · [revue de fond](docs/V02_TECHNICAL_AUDIT_20261012.md). Contenu **CLOSED_DOCUMENTARY_SCOPE**, aucune preuve de HA/PRA runtime revendiquée.
- **[Volume 03 — installation et exploitation](volumes/03-install-operate/README.md)** : rédaction ouverte après publication et contrôle du Volume 02.

Les anciennes éditions PDF restent disponibles dans [GitHub Releases](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases). La pagination reste informative; c'est la couverture technique vérifiée qui fixe la clôture.

## Historical Docker / Podman laboratory (20 October 2026)

The archived [Docker + Podman Masterclass](legacy/docker-podman-masterclass/README.md) is preserved intact in `legacy/docker-podman-masterclass/` with **31/31 source blobs and a [SHA manifest](legacy/docker-podman-masterclass-source-map.json)**. Its 10 labs and original license remain available independently of the Volume 01 text. This preservation does not prove container execution; the archived source was **manually deleted by its owner on 20 October 2026**, with 404 GitHub verification; **31/31 blobs remain intact on `main`**.
