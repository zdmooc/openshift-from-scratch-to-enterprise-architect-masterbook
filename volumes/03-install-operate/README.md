# Volume 03 — Installation et premières opérations OpenShift

**Statut : IN_PROGRESS · Début 12 octobre 2026, après clôture documentaire du Volume 02.**
**Version de référence : OpenShift Container Platform 4.22.**

## Chapitres disponibles

1. [Topologies et méthodes d'installation : choix d'architecture](01-topologies-and-installation-methods.md).
2. [Préflight d'infrastructure : DNS, load balancing, réseau et accès](02-infrastructure-preflight-dns-lb.md).

## Prochaines matières prévues, sans quota de pagination

- CRC/OpenShift Local : prérequis du poste, limites de ressources, activation et maintien propre.
- Single Node OpenShift : disque, installation et limites de résilience.
- Topologies multinœuds compactes et standard : rôles, quorum et domaines de panne.
- Installation bare metal / vSphere : IPI, UPI, Assisted et Agent-based selon support.
- Installation cloud et contraintes provider/permissions.
- Déploiement disconnected : miroir de release, images, catalogues et trust.
- Day-1 : inventaire, bootstrap, validation CVO/MCO, identités et sauvegarde initiale.
- Dossiers d'architecture, exercices corrigés et preuves reproductibles.

## Méthode et sécurité

Le volume part des contrats **réellement supportés par la version et le provider**, avant toute commande. Les exemples et préflights sont documentaires ou en lecture seule, avec contexte et résultats attendus. Aucune installation, destruction de VM, changement DNS/LB, rotation de certificat ni ajout de workload n'est exécuté sur le CRC dans cette itération.

Une première édition peut être publiée quand la couverture, la précision technique et les vérifications satisfont le [standard éditorial](../../docs/EDITORIAL_STANDARD.md), indépendamment de son nombre de pages.

[Atelier V03-L01 — matrice de préflight](../../labs/v03-01-installation-preflight-paper.md) · [Sources officielles 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installation_overview/ocp-installation-overview).
