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
