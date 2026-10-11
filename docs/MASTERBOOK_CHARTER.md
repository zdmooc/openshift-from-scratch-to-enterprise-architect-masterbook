# OCP-MB-I0 — Charte du Masterbook

**Statut : CADRAGE_INITIAL** · **Date : 2026-10-11** · **Responsable éditorial : Zidane Djamal**

## Mission

Construire une bible indépendante et évolutive d'OpenShift, du premier conteneur jusqu'aux arbitrages d'architecte d'entreprise, avec démonstrations vérifiables et pratiques Day-2. Le dépôt est le **livre-source**, non un remplacement des dépôts de démonstration.

## Public et parcours

| Parcours | Lecteur | Compétence à atteindre |
|---|---|---|
| P1 Foundations | Débutant, développeur, administrateur | Expliquer Kubernetes et utiliser les primitives OCP |
| P2 Build & Operate | Platform Engineer, administrateur | Concevoir, installer et opérer les capacités de base |
| P3 Resilience & Security | Tech Lead, SRE, sécurité | Sécuriser, observer, fiabiliser et dépanner |
| P4 Enterprise Architect | Architecte solutions / plateforme | Produire ADR, architecture de référence, NFR et trajectoires |

## Objectifs de qualité

1. Concepts expliqués sans dépendance à un cluster.
2. Schémas originaux, lisibles et exportables.
3. Commandes réversibles et préflight explicites; par défaut lecture seule.
4. Versions OpenShift, Kubernetes, API et Operators documentées.
5. Hypothèses, limites, modes de panne et alternatives explicités.
6. Exercices et attendus d'évaluation reproductibles.
7. Aucun secret ni information client/personnelle exporté depuis les labs.
8. Index des sources et attribution selon les droits réels.
9. Cas bancaires et assurance **anonymisés et conçus comme scénarios de référence** sauf preuve autorisée.
10. Distinction claire entre preuve locale CRC, comportement documenté et preuve production.

## Frontières

**Inclus** : plateforme OCP, réseau, stockage, IAM, sécurité, delivery, GitOps, Operators, SRE, résilience, industrialisation, FinOps/Green IT, architecture d'entreprise, IA sur OCP.

**Exclus** : reproduction intégrale de documentation tierce, copie des dépôts métiers, contenu marketing sans démonstration, promesses d'équivalence entre CRC et production.

## Gouvernance et statut des assertions

| Marquage | Sens | Exigence |
|---|---|---|
| PUBLIC_VERIFIED | Étayé par une source publique datée | URL, version, consultation |
| REFERENCE_ARCHITECTURE | Proposition conçue, non déployée | Hypothèses et compromis |
| INFERRED | Déduction ou estimation | Justification, validation attendue |
| RUNTIME_PROVEN | Résultat observé dans un environnement donné | Environnement, version, date, protocole, références de preuves |
| PLANNED | Contenu ou gate non encore réalisé | Action et critère de sortie |

Les termes **production-ready**, **certifié**, **supporté** ou **validé en production** sont interdits sans preuve correspondante.

## Chaîne de publication

Source Markdown → revue factuelle → revue technique → contrôle des droits et marques → validation des labs → gel d'édition → PDF/EPUB/HTML. Toute correction postérieure déclenche une nouvelle édition avec changelog.

## Définition de terminé pour un chapitre

- Objectifs pédagogiques clairs, public et prérequis.
- Explications et au moins un schéma ou modèle mental.
- Comparaison des solutions/compromis et modes de défaillance.
- Procédure d'observation ou atelier sécurisé si pertinent.
- Version et sources vérifiées, statut de preuve attribué.
- Vérifications de sécurité, droits d'auteur et terminologie réussies.
- Cohérence de navigation vers les volumes voisins.

Voir [EDITORIAL_STANDARD.md](EDITORIAL_STANDARD.md), [ROADMAP.md](ROADMAP.md) et [RIGHTS_AND_LICENSING.md](RIGHTS_AND_LICENSING.md).
