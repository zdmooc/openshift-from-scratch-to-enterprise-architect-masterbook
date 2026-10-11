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

## Erratum vérification de support OS OCP 4.22 (2026-10-11)

Attention : des pages officielles Red Hat 4.22 divergent sur l'emploi de RHEL pour les nœuds worker :
- [Notes de version 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes) : exigent RHCOS pour control plane et compute.
- [Architecture 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture) : indique RHEL possible sur certains workers.
- [Installing on any platform](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_any_platform/installing-platform-agnostic) : mentionne RHEL workers pour certaines installations.

Le Masterbook ne doit pas inférer une règle universelle à partir de l'une de ces pages contradictoires. Exiger une confirmation de support spécifique à la cible. Voir [l'erratum](ERRATA_V01_V02_20261011.md).


## Volume 02 — Machine API, OLM et CRD versioning (2026-10-11)

| Contrat vérifié | Documentation de référence |
|---|---|
| Machine, MachineSet, MachineHealthCheck et ControlPlaneMachineSet | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/index |
| ClusterAutoscaler, MachineAutoscaler et restrictions de provider | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/applying-autoscaling |
| Operator Lifecycle Manager (OLM) Classic | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/understanding-operators |
| OLM v1 : Catalogd, Operator Controller et ClusterExtension | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/extensions/architecture |
| OLM v1 : ClusterCatalog et catalogs Red Hat | https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/extensions/catalogs |
| CRD served/storage, webhook et stockage ancien | https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/ |

**Précautions** : les API Machine peuvent dépendre du type de cluster/provider; des fonctionnalités liées à Cluster API sont Technology Preview en 4.22. OLM Classic et OLM v1 ne partagent pas les mêmes objets d'API. Les fixtures de conversion sont hors cluster et ne prouvent pas le comportement d'un vrai admission server.
