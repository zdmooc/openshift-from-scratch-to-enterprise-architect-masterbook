# Volume 02 — Notes de l'édition 1.0 de contenu

**Édition : 11 octobre 2026 · Auteur : Zidane Djamal.**  
**Produit analysé : OCP 4.22 / Kubernetes 1.35.**

## Couverture

- 10 chapitres couvrant architecture interne API/etcd, scheduler/controller-manager, CVO, MCO, RHCOS, kubelet/CRI-O, admission, CRD, HA du control plane et N3.
- 2 ateliers : inventaire read-only et majorité mathématique d'etcd.
- 1 dossier de référence sur la résilience et les mises à jour de la plateforme bancaire.
- 16 tests offline de simulation de quorum, en complément des contrôles préexistants du dépôt.
- Glossaire dédié et références aux documentations officielles.

## Limites des preuves

- Aucun accès root ou cluster-admin, aucun nouveau workload CRC.
- Aucun redémarrage, test de perte de quorum, exécution de restore etcd ou mise à jour OpenShift.
- Les calculs de quorum sont mathématiques et ne représentent pas des observations de Raft en temps réel.
- Les SLO/RTO/RPO du dossier bancaire sont des **exigences à instruire**, pas des engagements démontrés.
- Les schémas Mermaid peuvent apparaître comme sources dans le premier PDF selon le moteur de publication.

## Droits

© 2026 Zidane Djamal pour ses textes et exemples originaux, sous réserve des droits des tiers. Aucune licence générale n'est présumée. OpenShift et Red Hat sont des marques de leurs titulaires. Cet ouvrage est indépendant et non affilié à Red Hat.

## Gouvernance de l'édition

Les sources Markdown font foi. Corriger la version 1.0 via errata/édition révisée plutôt que modifier silencieusement un fichier binaire publié. La génération PDF s'appuie sur un script versionné et une CI de vérification.


## Vérification de la publication

- [PDF édition 1.0 — 59 pages A4](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.0-20261011/OpenShift_Masterbook_Volume_02_Zidane_Djamal_2026.pdf).
- [GitHub Release](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.0-20261011).
- [CI de publication : SUCCESS](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38146269739).
- 68 tests Python offline et d'édition au total, 87 liens internes Markdown vérifiés.
- PDF : 199110 octets sur GitHub, texte extractible (111297 caractères par pypdf).
- Rendu des pages inspecté par échantillonnage visuel (couverture, sommaire, corps, annexes et glossaire).
- Diagrammes Mermaid conservés comme sources lisibles, non rendus en images.
- Aucun résultat ne prétend une qualification HA/PRA ou un restore etcd réel.

**La cible de pagination initiale de 200–280 pages reste un objectif d'approfondissement ultérieur, pas le compte réel de l'édition 1.0.**


## Révision 1.1 — approfondissements documentaires

Le manuscrit a été enrichi sur les dix chapitres : API/APF, Raft, scheduler, CVO, MCO, runtime, SCC/PSA, CRD, HA et N3. Un troisième laboratoire comporte 20 tests offline sur le filtrage de Pods. Quatre schémas SVG vectoriels originaux sont ajoutés. L'édition 1.0 reste immuable et les limites du contenu initial sont conservées dans ses notes de version.

Erratum vérifié : [ambiguïté de la documentation Red Hat OCP 4.22 sur les workers RHEL](ERRATA_V01_V02_20261011.md).
