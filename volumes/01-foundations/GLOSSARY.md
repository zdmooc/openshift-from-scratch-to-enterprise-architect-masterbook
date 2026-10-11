# Glossaire — Volume 01 (édition de travail)

| Terme | Définition opérationnelle |
|---|---|
| API server | Composant exposant l'API Kubernetes et appliquant authentification, autorisation et admission |
| Admission | Étape de validation/mutation de requêtes API selon configuration et politiques |
| Allocatable | Partie de capacité d'un nœud disponible pour le scheduling après réserves système |
| Cgroup | Hiérarchie Linux contrôlant et mesurant l'utilisation des ressources par groupe de processus |
| CNI | Interface entre runtime et plugin réseau, avec implémentations possibles différentes |
| Container | Instance de processus en environnement isolé, partageant ordinairement le noyau hôte |
| Controller | Logique observant l'état et essayant de rapprocher l'observé du désiré |
| CRD | CustomResourceDefinition : déclaration d'une extension d'API Kubernetes |
| CRI | Interface de communication entre kubelet et runtime de conteneur |
| CRI-O | Runtime de conteneur compatible CRI utilisé dans OpenShift |
| Digest | Identifiant cryptographique de contenu; n'identifie pas à lui seul un fournisseur fiable |
| Etcd | Base clé-valeur cohérente utilisée pour l'état persistant du control plane |
| Image index | Structure OCI qui peut référencer plusieurs manifests, par plateforme notamment |
| Kubelet | Agent de nœud qui coordonne l'exécution des Pods assignés |
| Limit | Plafond d'utilisation de ressources, avec enforcement dépendant de la ressource |
| Namespace Linux | Vue isolée de certains objets du noyau pour un groupe de processus |
| Namespace Kubernetes | Partition logique des objets API namespacés, non synonyme de namespace Linux |
| OLM | Operator Lifecycle Manager, mécanisme de gestion d'Operators add-on selon contexte |
| Operator | Controller encapsulant une expertise opérationnelle via API et reconcile loop |
| Pod | Plus petite unité déployable Kubernetes, contenant un ou plusieurs conteneurs liés |
| PV/PVC | Volume persistant et demande de stockage dans l'API Kubernetes |
| Reconciliation | Convergence entre état désiré et état observé, pas une garantie de réussite instantanée |
| Request | Besoin déclaré influençant la planification, la QoS et d'autres mécanismes |
| RHCOS | OS orienté conteneurs servant de fondation aux nœuds OpenShift |
| Route | Ressource OpenShift exposant un service via la couche ingress, selon configuration |
| SCC | Security Context Constraints : admission et restrictions de sécurité OpenShift |
| Scheduler | Composant qui sélectionne un nœud pour les Pods non assignés |
| SELinux | Contrôle d'accès obligatoire basé sur politiques et labels |
| Service | Abstraction Kubernetes fournissant un accès stable à un ensemble de backends |
| SLO | Objectif de niveau de service mesurable |
| OCI | Standards ouverts de format d'image, distribution et runtime de conteneurs |
| UID arbitraire | Modèle d'exécution où l'image doit fonctionner sous un UID non-root assigné dynamiquement |
