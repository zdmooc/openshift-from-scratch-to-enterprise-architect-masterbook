# Sources, versions et veille

**Consultation initiale : 2026-10-11.** Références privilégiées : éditeurs et projets officiels. Il ne s'agit pas d'une licence de recopie.

## Sources primaires pour l'édition de travail

| Sujet | Source |
|---|---|
| OpenShift 4.22 — architecture | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture |
| OpenShift 4.22 — control plane | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/control-plane |
| OpenShift 4.22 — Operators | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview |
| OpenShift 4.22 — présentation générale | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/overview/ocp-overview |
| Kubernetes — concepts | https://kubernetes.io/docs/concepts/ |
| Kubernetes — composants | https://kubernetes.io/docs/concepts/overview/components/ |
| Open Container Initiative — spécifications | https://opencontainers.org/ |
| OCI — image-spec | https://specs.opencontainers.org/image-spec/ |
| OCI — distribution-spec | https://specs.opencontainers.org/distribution-spec/ |
| OCI — runtime-spec | https://specs.opencontainers.org/runtime-spec/ |
| Linux — namespaces | https://man7.org/linux/man-pages/man7/namespaces.7.html |
| Linux — cgroup v2 | https://docs.kernel.org/admin-guide/cgroup-v2.html |
| Kubernetes — resources | https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/ |
| Kubernetes — scheduling | https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/ |
| Kubernetes — Deployments | https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ |
| Kubernetes — sécurité noyau | https://kubernetes.io/docs/concepts/security/linux-kernel-security-constraints/ |
| OpenShift 4.22 — Routes | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/ingress_and_load_balancing/routes |

## Politique version

- La documentation OpenShift **4.22** est la base de l'édition initiale, pas une affirmation que toute installation doit utiliser 4.22.
- Différencier **version de la documentation**, **version observée du labo** et **version cible**.
- Toute commande ou fonctionnalité marquée comme valable pour une version doit être revérifiée avant publication.
- Les pratiques support, Operator lifecycle, architectures HA et compatibilités entre versions nécessitent une source officielle actuelle.
- Traiter le matériel public externe comme preuve documentaire : **PUBLIC_VERIFIED**, et non comme lab **RUNTIME_PROVEN**.

## Veille éditoriale

À chaque nouvelle version OpenShift : relever les changements d'API, installation, architecture, Operators, sécurité, upgrades et documentation. Créer un delta par volume; éviter de changer silencieusement le sens d'un ancien laboratoire.

## À compléter

- Matrice API dépréciées / alternatives.
- Tableau de compatibilité Operators et produits avec dates de consultation.
- Index de citations au niveau des chapitres.
- Registre des figures et licences tiers.

## Sécurité et réseau — vérifications ajoutées en octobre 2026

| Sujet | Référence officielle |
|---|---|
| OpenShift 4.22 — SCC | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/managing-pod-security-policies |
| OpenShift 4.22 — PSA et interactions SCC | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/understanding-and-managing-pod-security-admission |
| OpenShift 4.22 — seccomp | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/security_and_compliance/seccomp-profiles |
| Kubernetes — NetworkPolicy | https://kubernetes.io/docs/concepts/services-networking/network-policies/ |
| Kubernetes — Server-Side Apply | https://kubernetes.io/docs/reference/using-api/server-side-apply/ |

Les contraintes d'admission sont évaluées à partir de l'environnement et des politiques effectives : elles ne sont pas prouvées par un validateur local de JSON.

## Réseau, stockage et diagnostic — édition Volume 01

| Sujet | Source officielle |
|---|---|
| DNS Operator OCP 4.22 | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/networking_operators/dns-operator |
| OCP 4.22 network security (policies composants critiques) | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html-single/network_security/index |
| OCP 4.22 networking overview | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html-single/networking_overview/index |
| OCP 4.22 storage | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/storage/index |
| DNS for Services and Pods | https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/ |
| PV/PVC | https://kubernetes.io/docs/concepts/storage/persistent-volumes/ |
| CSI VolumeSnapshots | https://kubernetes.io/docs/concepts/storage/volume-snapshots/ |
| Kubernetes debug service | https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/ |

La présence d'une source officielle ne prouve pas l'exécution d'un laboratoire. Les snapshots de volume n'apportent pas seuls de garantie de cohérence applicative.

## OCP 4.22 — version Kubernetes et RHCOS

Les [notes de version officielles](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes) indiquent Kubernetes 1.35 et CRI-O. Elles exigent RHCOS sur les nœuds du control plane et de calcul pour cette version. Ce point a été corrigé dans le chapitre 06.
