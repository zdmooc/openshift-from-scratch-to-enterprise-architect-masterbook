# Glossaire — Volume 02, architecture interne

| Notion | Sens opérationnel |
|---|---|
| API endpoint | Adresse exposant un serveur API Kubernetes/OpenShift aux clients autorisés |
| Admission | Contrôles pouvant muter, valider ou rejeter une requête API |
| APIService | Ressource permettant d'étendre certaines APIs via l'aggregation layer |
| CVO | Cluster Version Operator ; applique un payload de version et observe ses ClusterOperators |
| ClusterOperator | Objet de statut d'un opérateur fondamental OpenShift |
| ClusterVersion | Ressource décrivant version désirée et état actuel du cluster |
| CRD | CustomResourceDefinition : extension déclarative des types de ressources Kubernetes |
| CRI | Container Runtime Interface entre kubelet et runtime tel que CRI-O |
| CRI-O | Runtime de conteneurs compatible CRI d'OpenShift |
| CSR / CA | Demande de certificat / autorité de confiance de certificats |
| etcd | Stockage cohérent clé-valeur pour l'état de l'API de cluster |
| Finalizer | Entrave contrôlée à la suppression d'objet pour permettre un nettoyage |
| Ignition | Outil de configuration de première initialisation de RHCOS |
| kube-apiserver | API Kubernetes centrale, valide/autorise et persiste les ressources |
| kube-controller-manager | Groupe de contrôleurs Kubernetes fondamentaux |
| kube-scheduler | Sélectionne des nœuds pour les Pods non assignés |
| kubelet | Agent local de nœud observant et mettant en œuvre les Pods assignés |
| Lease | Objet de coordination, notamment pour l'élection de leader |
| MachineConfig | Description de modifications du système des nœuds |
| MachineConfiguration | Objet singleton de paramétrage du MCO pour certains comportements |
| MachineConfigPool | Groupe de nœuds convergeant vers une rendered configuration |
| MCO | Machine Config Operator ; gouverne certains changements système RHCOS |
| OLM | Operator Lifecycle Manager, gestion de certains Operators additionnels |
| OSUS | OpenShift Update Service, service proposant des chemins de mises à jour |
| PDB | PodDisruptionBudget ; borne certaines évictions volontaires |
| PSA | Pod Security Admission ; vérification de profils Pod Security Standards |
| Quorum | Majorité de votants requise dans le modèle de consensus Raft d'etcd |
| Raft | Algorithme de consensus utilisé par etcd |
| RHCOS | Red Hat Enterprise Linux CoreOS, système des nœuds OpenShift |
| Runlevel CVO | Ordonnancement de manifests de release selon dépendances |
| SCC | Security Context Constraint ; mécanisme OpenShift d'admission de sécurité Pod |
| SSA | Server-Side Apply ; mise à jour API avec propriété des champs |
| Storage version | Version de CRD persistée dans l'état Kubernetes |
| Served version | Version de CRD exposée aux clients |
| Webhook de conversion | Service externe traduisant des objets de CRD entre versions |
| Zone de panne | Domaine dont l'indisponibilité peut faire tomber plusieurs composants |

| Machine API | Gestion déclarative des Machines d'infrastructure, selon provider/support |
| Machine | Ressource OCP représentant un hôte/instance gérée et potentiellement liée à un Node |
| MachineSet | Contrôleur du nombre de Machines de calcul désirées |
| MachineHealthCheck | Détecte des Machines non saines et peut provoquer leur remplacement selon support |
| MachineAutoscaler | Bornes de Machines pour un MachineSet ciblé |
| ClusterAutoscaler | Décide du scaling de capacité selon Pods et limites configurées |
| ControlPlaneMachineSet | Gestion des Machines control plane sur plateformes compatibles |
| HPA | Ajuste des replicas de Pods, pas des Machines |
| OLM Classic | Cycle de vie add-on Operators fondé sur Subscription, CSV, InstallPlan et CatalogSource |
| OLM v1 | Cycle d'extensions via catalogd, Operator Controller, ClusterCatalog et ClusterExtension |
| CSV | ClusterServiceVersion, metadata/installation d'une version d'Operator Classic |
| OperatorGroup | Périmètre de watch/installation de plusieurs Operators Classic |
| InstallPlan | Plan calculé pour installer/mettre à jour des Operators Classic |
| CatalogSource | Source de packages et versions utilisable par OLM Classic |
| ClusterCatalog | Catalogue d'extensions OLM v1 |
| ClusterExtension | Ressource cluster-scoped de gestion d'une extension via OLM v1 |
| catalogd | Composant OLM v1 servant les métadonnées de File-Based Catalog |
| File-Based Catalog (FBC) | Représentation déclarative des packages, channels et bundles d'Operators |
| ConversionReview | Protocole API utilisé pour convertir des objets custom entre versions |
| storedVersions | Versions historiques pouvant rester physiquement stockées pour une CRD |
