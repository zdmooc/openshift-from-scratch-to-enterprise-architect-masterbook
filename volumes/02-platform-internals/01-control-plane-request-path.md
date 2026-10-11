# 01 — Anatomie d'une requête OpenShift : du client au control plane

**Volume 02 · DRAFT · Référence documentaire OCP 4.22 / Kubernetes 1.35.**  
**Preuve : PUBLIC_VERIFIED pour les mécanismes documentés. Aucun nouveau test CRC.**

## Objectifs

Comprendre ce que réalise chaque composant du plan de contrôle, expliquer pourquoi créer un Deployment ne signifie pas obtenir une application Ready, distinguer les refus d'authentification, d'autorisation et d'admission, et concevoir les premières étapes d'un diagnostic de l'API.

## 1. Un control plane est un système, pas seulement un nœud

| Composant | Rôle fondamental | Observation opérationnelle |
|---|---|---|
| kube-apiserver | Exposition de l'API Kubernetes et validation des demandes | Codes de réponse, latence, disponibilité |
| etcd | Conservation cohérente de l'état API | Quorum, membres, latence de persistance |
| kube-controller-manager | Exécution des contrôleurs Kubernetes standard | Ressources filles, Events, convergence |
| kube-scheduler | Sélection des nœuds pour les Pods non assignés | FailedScheduling et paramètres de placement |
| OpenShift API server | Gestion d'API propres à OpenShift | Disponibilité et cohérence d'API OpenShift |
| CVO | Pilotage du payload de release et ClusterOperators | Conditions de ClusterVersion |
| MCO | Configuration et mise à jour de systèmes RHCOS | MachineConfigPools, progression et dégradation |
| kubelet et CRI-O | Exécution de conteneurs sur les nœuds après placement | Status Pod, runtime et événements |

Pour OpenShift Container Platform 4.22, Red Hat documente Kubernetes 1.35, CRI-O et l'usage obligatoire de RHCOS pour les nœuds du plan de contrôle et de calcul. Les versions futures doivent être vérifiées séparément.

## 2. Chemin de la création d'un Deployment

L'ingénieur transmet une intention à l'API. La réponse HTTP positive de l'API indique que cette intention a été acceptée et persistée, pas que l'application traite déjà les transactions.

Séquence pédagogique :

1. Le client oc contacte l'endpoint API en HTTPS.
2. Le réseau et, selon topologie, le load balancer acheminent vers un kube-apiserver.
3. Authentification du sujet, puis autorisation et admission de l'objet.
4. Validation de la ressource et persistance de son état dans etcd.
5. Le Deployment controller observe le Deployment et ajuste un ReplicaSet.
6. Le ReplicaSet controller observe le ReplicaSet et ajuste des Pods.
7. Le scheduler choisit les nœuds des Pods non affectés.
8. Le kubelet observe les Pods assignés et demande à CRI-O de préparer leur exécution.
9. Les conditions Pod, ReplicaSet et Deployment reflètent ensuite l'état observé.
10. Le propriétaire métier évalue séparément les SLI de la transaction.

Les étapes 5 à 9 ne forment pas un programme séquentiel bloquant; elles représentent plusieurs boucles de contrôle asynchrones. Un Pod peut rester Pending, ou bien un container peut ne pas devenir Ready.

## 3. Le pipeline d'une demande API

Trois notions doivent être séparées :

- **Authentification** : établir l'identité technique du demandeur.
- **Autorisation** : déterminer si ce sujet peut réaliser le verbe demandé sur cette ressource et dans ce contexte.
- **Admission** : appliquer les validations/mutations supplémentaires, par exemple SCC, PSA, webhooks, LimitRange et politiques de quota selon configuration.

Un refus 403 lié à l'autorisation signifie qu'un serveur a pu traiter la requête et la refuser. Ce n'est pas, à lui seul, la preuve d'un control plane indisponible.

Dans une création de Pod, une autorisation RBAC positive ne suffit pas à garantir l'admission : l'objet peut encore être refusé pour profil de sécurité, quota ou validation webhook.

## 4. Persistance et événements d'état

Le kube-apiserver est le point d'entrée autorisé des changements; etcd conserve les ressources de l'API du cluster. Les contrôleurs surveillent ensuite les objets et reconcilient leur état.

Un changement de spec n'est pas une preuve de changement effectif des processus. Le statut peut avoir du retard, et le champ observedGeneration ne doit être interprété que selon le contrat de la ressource concernée.

Il faut aussi distinguer :

| Champ | Signification | Erreur courante |
|---|---|---|
| metadata.uid | Identité persistante d'un objet pendant sa vie | Confondre même nom et même objet |
| metadata.resourceVersion | Version opaque utilisée pour la concurrence et les observations | La traiter comme un timestamp |
| metadata.generation | Évolution de l'intention selon le type API | La confondre avec un nombre de retries |
| status / Conditions | Observations et raisons signalées | Conclure à un état réel sans vérifier sa fraîcheur |

## 5. List/watch et cohérence de la vue

Les clients de contrôleurs utilisent couramment un LIST initial suivi d'un WATCH des changements. Les caches peuvent avoir un retard transitoire. Les interruptions de watch, le vieillissement des versions historiques et le renouvellement des connexions impliquent une gestion de reprise.

Un changement accepté par l'API mais non encore présent dans un cache n'implique donc pas automatiquement une corruption etcd. Le diagnostic doit comparer plusieurs niveaux : réponse API, génération de l'objet, événements du contrôleur et statut des dépendances.

## 6. Qu'est-ce qu'une API hautement disponible ?

La disponibilité réelle repose sur plusieurs domaines :

- redondance des instances API et santé des certificats;
- endpoint DNS/LB joignable;
- disponibilité du quorum etcd;
- réseaux et stockage du control plane;
- capacité des nœuds de contrôle et de leurs ressources critiques;
- gestion du cycle de vie des certificats et updates.

La documentation OCP 4.22 indique trois nœuds de control plane pour les architectures de production standard, avec certaines topologies bare metal allant jusqu'à cinq. Il ne faut pas interpréter ce fait comme une autorisation universelle d'agrandir le control plane sans procédure supportée.

## 7. Gestionnaires actifs et élection de leader

kube-controller-manager et kube-scheduler utilisent des mécanismes de leader election dans des configurations HA afin de limiter l'activité concurrente sur les mêmes responsabilités. Les objets Kubernetes Lease sont une brique de coordination.

Ce mécanisme ne garantit pas l'absence de double effet dans une application qui appelle un système externe. Un Operator bancaire doit concevoir séparément idempotency keys, retries et éventuellement fencing pour les opérations métier.

## 8. Lecture seule : premiers contrôles

Dans un cluster OpenShift autorisé, relever :

- la version client/cluster et l'état de ClusterVersion ;
- les conditions Available, Progressing et Degraded des ClusterOperators ;
- la santé des nœuds, leurs domaines de panne et leur rôle ;
- l'état des MachineConfigPools ;
- les Pods du plan de contrôle visibles dans les namespaces système ;
- les événements associés aux workloads impactés.

Exemples de commandes en lecture seule :

    oc version
    oc get clusterversion
    oc get clusteroperators
    oc get nodes -o wide
    oc get machineconfigpools
    oc -n openshift-etcd get pods
    oc -n openshift-kube-apiserver get pods

Des erreurs RBAC peuvent limiter l'observation. N'essayez pas d'obtenir une session privilégiée ou d'éditer le control plane pour un exercice de diagnostic.

## 9. Lecture de symptômes

| Symptôme | Pistes à départager |
|---|---|
| Échec de négociation TLS de l'API | DNS, load balancer, certificat, CA, endpoint |
| API renvoie Forbidden | Sujet, verbes RBAC, namespace, ressource |
| Pod refusé à la création | Admission SCC/PSA, webhook, quota, LimitRange |
| Pod Pending sans affectation de nœud | Scheduler, requests, taints, PVC et topology |
| Pod assigné mais ImagePullBackOff | Référence d'image, registre, réseau, secret de pull |
| Deployment créé, replicas non prêts | Contrôleurs, scheduler, kubelet, probes |
| CVO Progressing anormalement | Version, ClusterOperators, MCO et dépendances |

## 10. Questions d'architecte

1. Pourquoi le kube-apiserver ne lance-t-il pas lui-même les containers ?
2. Quelle différence entre une écriture API acceptée et une condition Ready ?
3. Pourquoi etcd n'est-il pas une base de données applicative ?
4. Quelles couches doivent être disponibles pour une API réellement hautement disponible ?
5. Un rôle RBAC suffisant garantit-il l'admission d'un Pod ?
6. Pourquoi le scheduler n'est-il pas responsable de télécharger les images ?
7. Comment distinguer panne d'API, problème d'authentification et manque de droits ?

## Sources officielles

- [Red Hat — OCP 4.22 Architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — OCP 4.22 Control plane](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/control-plane)
- [Red Hat — OCP 4.22 Release notes](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes)
- [Kubernetes — Cluster architecture](https://kubernetes.io/docs/concepts/architecture/)
- [Kubernetes — API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Kubernetes — Leases](https://kubernetes.io/docs/concepts/architecture/leases/)

**Limite de preuve :** chapitre documentaire ; aucun nouveau test sur un cluster réel pendant cette rédaction.
