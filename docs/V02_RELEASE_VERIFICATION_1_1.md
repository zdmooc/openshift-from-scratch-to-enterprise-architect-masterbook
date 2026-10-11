# Volume 02 — vérification PDF, édition 1.1

**Date : 2026-10-11 · Statut : publié et vérifié.**

| Contrôle | Résultat |
|---|---|
| GitHub release | [v02.1-20261011](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.1-20261011) |
| PDF | [Télécharger](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.1-20261011/OpenShift_Masterbook_Volume_02_Edition_1_1_Zidane_Djamal_2026.pdf) |
| Pages | **85 A4** |
| Taille PDF de l'asset GitHub | **317311 octets** |
| SHA-256 du PDF extrait de l'artefact CI | **9d8e072198495fe1f09972653c66bfc424a8ed22afd08b3fa1df292d5e3b6668** |
| Texte extractible selon CI/pypdf | **176407 caractères** |
| Tests Python hors cluster + édition | **94 tests réussis** |
| Liens Markdown locaux | **91 contrôles réussis** |
| Schémas vectoriels originaux ajoutés | **4 fichiers SVG** |
| CI de publication | [SUCCESS](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38149733777) |
| Inspection visuelle | Pages 1–4, 8, 17, 30, 45, 58, 70, 84 et 85 |
| Pages sans texte extractible | **0** |
| Exécution sur CRC | **Aucune nouvelle intervention** |

## Résultat de la revue

Le document est typographié en A4 avec couverture, sommaire, tableaux, blocages de code et diagrammes SVG rendus. Les pages inspectées ne révèlent pas de découpe manifeste ni de chevauchement apparent. L'inspection visuelle est un **échantillonnage**, pas une relecture humaine exhaustive des 85 pages.

## Limites techniques et éditoriales

- L'édition 1.1 augmente de **59 à 85 pages**, mais n'atteint pas les 200–280 pages initialement envisagées.
- Les quatre diagrammes SVG sont intégrés au PDF; les autres blocs Mermaid restent affichés sous forme de code, faute de rendu graphique complet.
- Les simulations Python du scheduler et du quorum etcd ne reproduisent pas un scheduler Kubernetes réel ni un consensus Raft exécuté.
- Aucune restauration etcd, panne contrôlée de master, upgrade CVO/MCO, admission réelle de CRD ni test de HA/PRA n'a été pratiqué.
- Les deux versions publiées 1.0/1.1 sont conservées et les corrections de support OS figurent dans [l'erratum](ERRATA_V01_V02_20261011.md).

L'édition 1.1 est une **publication technique révisée**, pas encore la version exhaustive/définitive promise à terme.
