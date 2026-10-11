# Volume 02 — OpenShift Platform Internals

**Statut : IN_PROGRESS — ouvert après publication du PDF Volume 01**  
**Base : OpenShift Container Platform 4.22 et Kubernetes 1.35.**

## Chapitres disponibles

1. [Chemin d'une requête API et architecture du control plane](01-control-plane-request-path.md).
2. [etcd : cohérence, quorum, sauvegarde et reprise](02-etcd-consistency-and-recovery.md).

## Suite rédactionnelle

- Scheduler, controller-manager et Leases.
- OpenShift API server, Cluster Version Operator et statut des ClusterOperators.
- RHCOS, Ignition et Machine Config Operator.
- kubelet, CRI-O, cycle de vie des Pods.
- Admission et extensibilité des APIs.
- Architecture haute disponibilité et diagnostic N3 du control plane.

Les opérations de restauration ne sont pas exécutées sur CRC. Les modes de panne et les plans de récupération sont expliqués, mais aucune preuve runtime nouvelle n'est revendiquée.
