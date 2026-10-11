# Volume 01 — état de l'édition 1.0

**Date : 2026-10-11. Couverture éditoriale de base : complète.**

| Élément | Périmètre | État |
|---|---|---|
| Chapitres techniques | 13 | EDITION_1_CONTENT_COMPLETE |
| Cas bancaires | 3 | REFERENCE_ARCHITECTURE, non déployés |
| Laboratoires | 8 | 5 procédures/paper labs ; 3 ensembles de tests hors cluster |
| Tests automatisés | 42 | Python offline en CI, non validés par Kubernetes |
| PDF | 13 chapitres + études + ateliers + glossaire | PUBLIÉ : 109 pages, CI success, texte extractible |
| Cible documentaire | OpenShift 4.22 / Kubernetes | Documentation publique, état de support à revérifier |

## Limitations importantes

- Aucun nouveau test CRC n'a été exécuté pour produire cette édition.
- Aucune preuve de HA multinœud, PRA, restauration de données, performance sous charge ou conformité réglementaire n'est revendiquée.
- Les exemples `.invalid`, digests fictifs et scripts de triage sont **pédagogiques** et ne peuvent pas être assimilés à des ressources validées en production.
- 42 tests offline passent dans GitHub Actions, mais ne réalisent aucune admission OpenShift, aucun scheduling, aucun scan d'images et aucun déploiement.
- Les droits sur les matériaux tiers et le choix d'une licence générale restent distincts du copyright applicable aux créations originales.
- L'objectif initial de 180–240 pages était indicatif; le PDF comporte exactement le nombre de pages du contenu réel mis en page, sans remplissage artificiel.

## Chaîne d'édition

Markdown → revue de la couverture et tests Python offline → liens locaux → PDF → contrôle pages / extraction → diffusion avec notes de version.

[Sommaire complet](../volumes/01-foundations/README.md) · [Build PDF](../scripts/build_volume01_pdf.py) · [Notes d'édition](V01_RELEASE_NOTES.md).

Le Volume 02 a démarré **après** publication et inspection du PDF de 109 pages du Volume 01.


[PDF Volume 01](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v01.0-20261011/OpenShift_Masterbook_Volume_01_Zidane_Djamal_2026.pdf) · [Compte rendu de vérification](V01_RELEASE_VERIFICATION.md).
