# V02-L03 — Filtrage scheduler : simulation déterministe sans cluster

**Mode : OFFLINE_TEST · 20 tests Python · Aucun accès kubeconfig, réseau ou cluster.**

## 1. Problème

On doit placer un Pod fictif de 1000m CPU et 1024 MiB. Deux workers présentent des requests déjà engagées et des taints. L'objectif est de comprendre **pourquoi le scheduler peut rejeter des nœuds alors que le CPU instantané semble faible**.

### Exemple de nœuds

| Nœud | CPU allocatable | CPU déjà demandé | Taint | Éligibilité pour Pod 1000m |
|---|---:|---:|---|---|
| worker-a | 4000m | 3500m | Aucun | Non : manque 500m |
| worker-b | 8000m | 4000m | reserved | Non : taint non toléré |

Le résultat est zéro nœud éligible, même si les deux nœuds sont Ready.

## 2. Exécution hors cluster

Depuis la racine du dépôt :

~~~bash
python -m examples.v02.scheduling_filter examples/v02/cases/fit-and-taint.json
python -m unittest discover -s tests -p "test_v02_scheduling_filter.py" -v
~~~

L'application n'utilise que la bibliothèque standard de Python. Les tests modifient uniquement des objets en mémoire. Les limites du modèle sont inscrites dans la sortie et dans le code.

## 3. Exercices

**E1 — Un seul filtre bloque :** ajouter \`reserved\` aux tolerations. Le worker-b devient éligible à l'étape de filtrage illustrée, sans garantie que Kubernetes le choisira.

**E2 — Request CPU :** passer la request Pod de 1000m à 100m. Le worker-a devient éligible, mais la taint continue de bloquer worker-b. Attention : diminuer une request sans mesurer la consommation réelle peut dégrader les performances.

**E3 — Sélecteur erroné :** imposer \`node_selector.pool=gpu\`. Aucun des workers étiquetés \`apps\` ne correspond. Une ressource libre ne compense pas un selector impératif.

**E4 — Zone :** autoriser \`reserved\` mais n'autoriser que la zone \`a\`. Le worker-b échoue cette fois sur la contrainte de zone, ce qui montre l'importance du domaine de panne.

## 4. Limites de validité

Le simulateur **n'implémente pas** kube-scheduler : pas de scoring, Pod topology spread effectif, CSI, liens de volumes, hostports, priorité, préemption, queueing, Pods Overhead ou réel binding. Les taints sont représentés comme des chaînes simples, pas des objets Kubernetes dotés d'un effect. Aucun résultat ne peut être qualifié RUNTIME_PROVEN.

## 5. Corrigé de soutenance

Une décision de placement dépend de plusieurs filtres indépendants. Un \`oc top nodes\` montrant une faible utilisation n'invalide pas un échec \`Insufficient cpu\` : les valeurs demandées, et non seulement l'utilisation actuelle, gouvernent la disponibilité logique pour un nouveau Pod.

En production, confronter le modèle aux Events du scheduler et à la spec réelle des ressources sur un environnement autorisé, sans modifier les nœuds ou les taints simplement pour satisfaire un exercice.

## Sources

- [Kubernetes — Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
- [Kubernetes — Taints/Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Kubernetes — Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
