# Lab V02-L01 — Inventaire du control plane sans mutation

**Mode : DOCUMENTED_NOT_RUN · Lecture seule · Aucune charge nouvelle sur CRC**

## Prérequis

- Accès à un cluster autorisé et client oc configuré.
- Droits appropriés de lecture des ressources du cluster.
- Aucun accès aux secrets, dumps etcd, certificats privés ou debug privilégié nécessaire.

## Contrôles

~~~bash
oc config current-context
oc version
oc get clusterversion
oc get clusteroperators
oc get nodes -o wide
oc get machineconfigpools
oc -n openshift-etcd get pods
oc -n openshift-kube-apiserver get pods
oc -n openshift-kube-controller-manager get pods
oc -n openshift-kube-scheduler get pods
~~~

Cette procédure ne modifie pas le cluster. Cependant, elle peut produire des noms/IP internes : ne pas publier une sortie brute sans anonymisation.

## Restitution attendue

| Contrôle | Questions | Limite |
|---|---|---|
| Version | Quelle version est indiquée ? Est-ce le plan prévu ? | La version ne prouve pas le support de toutes les fonctionnalités |
| ClusterOperators | Available / Progressing / Degraded ? | Conditions ne prouvent pas le parcours métier |
| Nodes | Rôles et domaines de panne visibles ? | Labels ne prouvent pas l'indépendance physique |
| MCP | Updated/Updating/Degraded ? | État MCO, pas performance applicative |
| Pods etcd | Instances Running/Ready ? | Ne prouvent pas seuls le quorum |
| API Pods | Instances listées ? | Ne prouvent pas tous les chemins LB/TLS |
| Scheduler | Pods en activité ? | Ne prouvent pas l'absence de Pods Pending |

## Questions d'architecte

1. Quelle différence entre kube-apiserver et OpenShift API server ?
2. Comment mesurer une perte d'API depuis le point de vue d'un client ?
3. Pourquoi un cluster mono-nœud ne prouve-t-il pas la HA ?
4. Quel signal montre qu'un MCP ne converge pas ?
5. Quelles conditions faut-il réunir avant un upgrade ?

Ce lab n'a pas été exécuté pendant la rédaction. Ne pas compléter les cases par des valeurs fictives.
