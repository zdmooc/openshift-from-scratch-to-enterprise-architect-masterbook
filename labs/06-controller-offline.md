# L06 — Simulateur de réconciliation et tests de panne (sans cluster)

**Mode : OFFLINE_TESTABLE · Python 3.10+ · Standard library uniquement.**  
**Statut : exemples disponibles, exécution locale non vérifiée au moment de la publication.**

## 1. Ce que le lab démontre

Une simulation déterministe de l'algorithme de convergence avec deux ressources filles, Deployment et Service. Elle permet de tester :

- création puis deuxième reconcile sans écriture supplémentaire;
- panne de Service après la création du Deployment, suivie d'une reprise;
- correction d'un drift de champ possédé sans effacer une annotation tierce;
- conditions d'attente puis de readiness;
- politique de suppression Retain ou Delete;
- refus d'écraser une ressource possédée par un autre acteur;
- rejet d'un contrat invalide avant toute écriture;
- mise à jour logique de la génération observée.

**Ne pas confondre** ces vérifications avec des tests Kubernetes : aucune API Kubernetes, aucun RBAC réel, aucune admission SCC, aucun watch, aucun SSA, aucun CRI-O, ni aucune élection de leader ne sont simulés.

## 2. Reproduction

Depuis la racine du dépôt, dans Python 3.10 ou plus récent :

~~~bash
python -m examples.v01.reconcile_simulator
python -m unittest discover -s tests -p "test_*.py" -v
~~~

Sous Git Bash Windows, `python` doit pointer vers l'interpréteur Python installé. Aucune dépendance pip et aucun cluster connecté ne sont nécessaires. Le simulateur n'accède ni au disque ni au réseau, hormis les lectures normales du code source par Python.

## 3. Interprétation des résultats

Le premier reconcile provoque conceptuellement deux écritures, et renvoie **Progressing** car aucun replica n'est marqué prêt. Le second reconcile ne doit produire aucune écriture. Après changement de `ready_replicas` à 2, le statut passe à **Ready** sans déployer une nouvelle ressource.

La suite `unittest` couvre au moins dix invariants. Un test vert atteste **uniquement du modèle enseigné** ; il ne qualifie pas un Operator pour production.

## 4. Exercices complémentaires

**E1 — Reconcile partiel.** Ajouter un troisième objet ConfigMap et provoquer une panne sur sa création. Vérifier que les deux premiers objets ne sont pas recréés.

**E2 — Drift inverse.** Modifier une annotation possédée par un tiers. Vérifier qu'aucune mise à jour ne l'écrase. Documenter le contrat de propriété des champs.

**E3 — Redéploiement.** Passer generation de 1 à 2 et image d'une valeur à une autre. Observer l'unique écriture attendue dans la ressource Deployment.

**E4 — Gestion des erreurs.** Différencier permission refusée, erreur transitoire et rejet de validation. Expliquer pourquoi leurs Conditions et stratégies de retry ne devraient pas être identiques dans un Operator réel.

## 5. Passage au monde réel

Le Volume 08 traduira ces invariants dans controller-runtime : reconcile avec client Kubernetes, cache, errors, conditions, Envtest, Kind, SSA, RBAC et Lease. La validation d'un vrai Operator sur CRC exige des preuves de version et de contexte distinctes de ce laboratoire offline.

## Sources

- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Kubernetes — API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
