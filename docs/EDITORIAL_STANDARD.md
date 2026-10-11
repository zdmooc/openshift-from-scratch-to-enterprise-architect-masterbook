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

## Décision éditoriale basée sur le fond (aucune cible de pages)

La pagination, le décompte de mots, les schémas et les tests sont des **métriques de production**, pas des objectifs. Ne pas allonger artificiellement un chapitre, découper une matière sans logique ni déclarer qu'un livre est incomplet simplement parce qu'il est plus court qu'une estimation initiale.

### Matrice d'acceptation d'un volume

| Gate | Condition de sortie fondée sur le contenu | Échec typique |
|---|---|---|
| C1 — Couverture | Tous les thèmes obligatoires du volume ont une explication et une frontière avec les autres volumes | Sujet important évoqué dans le sommaire mais absent |
| C2 — Profondeur | Les mécanismes, états, flux, alternatives, erreurs et limites sont intelligibles | Généralités sans mécanique ni exemple discriminant |
| C3 — Véracité | Assertions sensibles à la version vérifiées, divergences officielles et errata traités | Compatibilité/support affirmé sans vérification |
| C4 — Reproductibilité | Exemples cohérents avec leur portée; exercices ou procédures et critères de résultat expliqués | Commandes non exécutables présentées comme testées |
| C5 — Preuve | Chaque résultat revendiqué est accompagné de statut et de preuve adaptée | Simulation offline présentée comme test runtime |
| C6 — Sécurité/IP | Aucun secret, PII ni reproduction non autorisée; scénarios à risque encadrés | Dump de cluster, clé ou code tiers sans droit |
| C7 — Édition | Terminologie, navigation, figures, citations et rendu lisibles | PDF publiable mais sommaire ou figures incorrects |

**FINAL** est autorisé lorsque C1–C7 sont satisfaits, plus les gates G1/G2/G4/G5 (et G3 pour toute preuve RUNTIME_PROVEN effectivement revendiquée). Une édition intermédiaire peut être publiée avant FINAL, avec un registre précis des lacunes de fond.

Pour un lab non exécuté, la rédaction peut être complète si son statut **DOCUMENTED_NOT_RUN** est visible, que les étapes ne mettent pas en danger un cluster partagé, et que l'absence de validation n'est pas cachée. Exiger un lab destructif réel pour atteindre un quota de tests serait contraire à cette politique.

### Revue « substance ou remplissage ? »

Un ajout est recevable s'il répond à une question technique nouvelle, réfute une confusion répandue, apporte un mécanisme causal, présente un cas réel correctement borné, permet un test ou justifie un choix d'architecture. Il est à réécrire ou supprimer s'il répète un chapitre, amplifie la formulation sans notion supplémentaire, ou fabrique une preuve non obtenue.

## Relecture

**G1 — Editorial** : clarté, progression, terminologie, index.  
**G2 — Technical** : version, sources, mécanismes, commandes.  
**G3 — Runtime** : lab exécuté dans un environnement déclaré, si requis.  
**G4 — Security/IP** : retrait secrets/PII, autorisations, attribution.  
**G5 — Release** : navigation, lien, build et changement d'édition.

Aucun statut **FINAL** sans G1/G2/G4/G5, et G3 pour les chapitres revendiquant RUNTIME_PROVEN.

## Gestion des révisions

Les mises à jour suivent l'ordre : source officielle → analyse d'impact → errata → patch chapitres/labs → validation → publication. Les changements de version majeurs doivent figurer dans un registre de compatibilité.
