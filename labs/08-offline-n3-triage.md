# L08 — Simuler un triage N3 : symptômes, hypothèses et preuves

**Statut : OFFLINE_TEST · Sans cluster ni réseau · Python 3.10+**

## Objectif

Construire un **arbre de vérification**, pas une remédiation automatique. Les quatre jeux de données JSON sont des cas entièrement fictifs : aucun nom client, adresse réelle, token ou sortie de cluster.

## Exécution depuis la racine du dépôt

~~~bash
python -m examples.v01.n3_triage examples/v01/incident-cases/no-endpoints.json
python -m examples.v01.n3_triage examples/v01/incident-cases/pending-storage.json
python -m examples.v01.n3_triage examples/v01/incident-cases/dns-degraded.json
python -m examples.v01.n3_triage examples/v01/incident-cases/selector-mismatch.json
python -m unittest discover -s tests -p "test_*.py" -v
~~~

Le moteur conserve les signaux contradictoires au lieu de conclure à une cause unique. \`NO_READY_ENDPOINTS\` et \`DNS_OPERATOR_DEGRADED\` peuvent apparaître ensemble sans implication causale prouvée.

## Cas et corrigé

| Cas | Observations | Premières vérifications |
|---|---|---|
| LAB-N3-001 | Route, 0 endpoint, probe échoue | Selector Service, readiness, port |
| LAB-N3-002 | Pod/PVC Pending, FailedMount | StorageClass, CSI, Events, topology |
| LAB-N3-003 | DNS Operator Degraded mais endpoints présents | Corréler une vraie défaillance de résolution |
| LAB-N3-004 | Pods prêts et selector Service incorrect | Corriger hypothèse de sélection, ne pas toucher TLS |

Le moteur **ne contacte pas l'API OpenShift**, ne déploie rien, n'ouvre pas de réseau et ne lit pas de kubeconfig. Ses résultats sont des pistes pédagogiques. Les tests négatifs rejettent schémas incomplets, nombres invalides et clés inattendues.

## Pour passer du lab à l'exploitation

Exiger un accès RBAC autorisé; collecter des métriques horodatées expurgées; confronter chaque hypothèse aux Events, Conditions et traces. Une action sur la plateforme nécessite un changement approuvé et un plan de retour arrière. Ce laboratoire ne valide pas l'exécution d'une remédiation réelle.

## Sources

- [Kubernetes — Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Kubernetes — Debug Service](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
