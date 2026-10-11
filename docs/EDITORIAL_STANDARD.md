# Standard éditorial et contrat des chapitres

## Modèle de chapitre

Chaque chapitre possède un bandeau de métadonnées :

~~~yaml
volume: "01"
chapter: "01"
title: "OpenShift : pourquoi et pour quoi faire ?"
status: "DRAFT"
scope_version: "OpenShift Container Platform 4.22"
evidence_level: "PUBLIC_VERIFIED"
last_verified: "2026-10-11"
~~~

Le corps suit cet ordre :

1. Objectifs, prérequis, publics et critères d'acquisition.
2. Le problème à résoudre avant d'introduire la technologie.
3. Concepts, glossaire et mécanisme causal.
4. Architecture (avec Mermaid ou schéma original).
5. Séquences, flux et cas d'utilisation.
6. NFR, coûts, sécurité, risques et trade-offs.
7. Pas-à-pas en lecture seule, puis exercices mutateurs isolés si autorisés.
8. Résultats attendus, commandes de vérification et nettoyage.
9. Interview / revue d'architecture avec réponses argumentées.
10. Sources, versions, limitations, preuves et statut.

## Politique des commandes

- Par défaut : **read-only**. Pas de modifications de cluster, de secrets, de workloads ni de suppression sans opt-in.
- Distinguer commandes qui s'exécutent localement de celles qui contactent un API server.
- Ne jamais écrire des jetons, kubeconfigs, clés privées ou identifiants utilisateurs dans la sortie du livre.
- Pour tout atelier mutateur : namespace dédié, préflight, quota, plan de retour arrière, budget CPU/RAM, cleanup et vérifications.
- Les sorties réelles sont pseudonymisées et datées. Des sorties fictives sont étiquetées **ILLUSTRATIVE_ONLY**.

## Architecture et assertions

Rattacher les diagrammes aux composants et flux réels. Une référence à un dépôt n'est pas une preuve d'exécution. RUNTIME_PROVEN exige : date + version + environnement + commande/protocole + capture/artefact + état observé.

Toute affirmation de compatibilité avec une version doit être contrôlée dans la documentation de cette version. Toute contrainte support/produit/HA doit être revue au moment de publication.

## Relecture

**G1 — Editorial** : clarté, progression, terminologie, index.  
**G2 — Technical** : version, sources, mécanismes, commandes.  
**G3 — Runtime** : lab exécuté dans un environnement déclaré, si requis.  
**G4 — Security/IP** : retrait secrets/PII, autorisations, attribution.  
**G5 — Release** : navigation, lien, build et changement d'édition.

Aucun statut **FINAL** sans G1/G2/G4/G5, et G3 pour les chapitres revendiquant RUNTIME_PROVEN.

## Gestion des révisions

Les mises à jour suivent l'ordre : source officielle → analyse d'impact → errata → patch chapitres/labs → validation → publication. Les changements de version majeurs doivent figurer dans un registre de compatibilité.
