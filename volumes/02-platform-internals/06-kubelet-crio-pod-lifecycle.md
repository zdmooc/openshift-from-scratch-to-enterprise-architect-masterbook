# 06 — kubelet, CRI-O, runtime OCI et cycle de vie d'un Pod

**Volume 02 · DRAFT · OpenShift 4.22 / Kubernetes 1.35**  
**Objectif : comprendre ce qui se passe après le scheduling, jusqu'aux statuts observables.**

## 1. La frontière entre API et OS de nœud

Le kube-apiserver stocke l'état demandé. Le scheduler choisit le nœud. Le **kubelet** de ce nœud surveille les Pods assignés et cherche à les faire fonctionner. Il s'appuie sur l'interface **Container Runtime Interface (CRI)** pour demander au runtime CRI-O de créer ou arrêter des conteneurs.

CRI-O utilise ensuite les mécanismes de runtime OCI, le stockage d'images et les ressources du noyau Linux. Selon le contexte, l'implémentation OCI bas niveau peut employer crun/runc; l'architecture se décrit par contrats, pas par un nom d'exécutable universel.

~~~mermaid
flowchart TD
  API[API server : PodSpec] --> K[kubelet du noeud]
  K --> CRI[CRI via gRPC]
  CRI --> C[CRI-O]
  C --> IMAGE[Images / registry]
  C --> OCI[Runtime OCI]
  OCI --> NS[Linux namespaces / cgroups]
  OCI --> SEC[SELinux / seccomp / capabilities]
  NS --> PROC[Processus applicatif]
  SEC --> PROC
  K --> STATUS[PodStatus / Events]
  STATUS --> API
~~~

Ce schéma représente les responsabilités. L'ordre de montage des volumes, configuration réseau et création de sandboxes varie selon l'implémentation.

## 2. Le Pod sandbox et le partage de réseau

Plusieurs containers d'un même Pod partagent normalement le namespace réseau, donc les ports et l'adresse IP du Pod. Ils peuvent communiquer via localhost et échanger des volumes montés en commun selon la spec. Cela ne signifie pas que deux Pods partagent les mêmes processus ou fichiers.

Une erreur « address already in use » peut survenir lorsque deux containers d'un Pod tentent d'écouter le même port. En revanche, deux Pods différents peuvent exposer le même containerPort sans conflit si leurs namespaces réseau sont séparés.

Les exceptions utilisant hostNetwork ou hostPort ont des conséquences de placement et de sécurité; elles ne doivent pas être ajoutées simplement pour éviter de configurer un Service.

## 3. Image pull et création des conteneurs

Étapes conceptuelles :
1. le kubelet observe le Pod assigné;
2. le runtime identifie les références d'images et les éventuels pull secrets;
3. le registre est joint, l'image est résolue et ses blobs sont obtenus/présents en cache;
4. les sandboxes, namespaces, mounts et conditions réseau sont préparés;
5. le runtime OCI démarre le processus;
6. kubelet observe exits, restarts et health probes;
7. le statut est publié à l'API.

Un \`ErrImagePull\` / \`ImagePullBackOff\` indique un problème antérieur au démarrage applicatif effectif. Il peut provenir d'un nom d'image erroné, d'une authentification manquante, de DNS, proxy, CA, connectivité ou du registre.

Un \`CrashLoopBackOff\` concerne des redémarrages d'un container qui a déjà tenté de démarrer. Les messages logs/termination state et les probes sont alors essentiels.

## 4. UID, permissions, SELinux et seccomp

Même si une image a été construite par Docker/Buildah/Podman, le cluster impose ses propres conditions de sécurité. Dans OpenShift, la SCC retenue peut déterminer ou contraindre l'UID. Une image nécessitant un UID fixe arbitraire peut échouer à l'admission ou au runtime.

Il faut séparer :
- **admission** : PodSpec refusée avant création;
- **création runtime** : container ne démarre pas faute de permission/mount;
- **exécution applicative** : binaire démarre puis échoue à lire ou écrire;
- **probe** : application tourne mais n'est pas considérée Ready.

L'architecture recommande de construire des images compatibles avec des UID non-root et d'éviter des chemins d'écriture dépendants de root. Un chmod 777 ne constitue pas une mesure de sécurité acceptable par défaut.

## 5. Requests, limites et cgroups

Les requests guident le scheduling et l'allocation relative de certaines ressources; les limits plafonnent la consommation selon le contrôleur concerné. Pour CPU, un quota peut causer du throttling; pour mémoire, l'atteinte de la limite peut provoquer une terminaison OOM.

Sur Linux avec cgroup v2, des fichiers comme cpu.stat, cpu.max, memory.current et memory.events donnent des indices. Leur disponibilité depuis un container dépend du montage et des permissions. Sur Windows Git Bash, ces chemins ne décrivent pas directement le noyau RHCOS du CRC.

### Incident : CPU à 20 % sur le nœud et p99 très élevé

Il peut s'agir de throttling local malgré une consommation globale modérée, d'un pool DB saturé ou de congestion externe. Le diagnostic compare les métriques de throttling par container, l'usage CPU par fenêtre, les latences et les dependances.

## 6. Init containers, sidecars et lifecycle

Les init containers classiques s'exécutent avant les containers applicatifs; un échec peut empêcher le Pod de progresser. Les modèles de sidecars natifs peuvent suivre une sémantique de lifecycle différente, liée aux types et champs de la version Kubernetes.

La séquence des hooks et la gestion des signaux importent :
- postStart intervient autour du démarrage du container;
- preStop peut précéder l'arrêt gracieux;
- SIGTERM permet au processus de drainer ses requêtes;
- un SIGKILL peut survenir à l'expiration du délai de grâce.

L'architecte doit documenter le comportement en présence de connexions long-lived, MQ consumers et transactions in-flight. Un Pod disparu ne garantit pas qu'un message ait été acquitté de manière atomique.

## 7. Readiness, liveness et startup probes

| Probe | Effet | Risque de configuration |
|---|---|---|
| startupProbe | Protège une phase de démarrage lente avant autres probes | Seuil trop bas causant restart loop |
| readinessProbe | Détermine l'éligibilité aux Services | Sonde superficielle qui masque échec métier |
| livenessProbe | Décide de redémarrer un container défaillant | Redémarrer en boucle en cas de panne externe |

Une liveness fondée directement sur l'accessibilité d'une base externe est risquée : lors d'une panne de base, tous les Pods risquent de redémarrer, aggravant l'incident. La readiness et une stratégie de dégradation sont généralement plus pertinentes pour signaler l'incapacité temporaire à servir des requêtes.

## 8. Cycle d'arrêt et évictions

Les Pods ont une période de terminaison gracieuse. Des changements de Deployment, drains ou suppressions peuvent provoquer un shutdown; les applications doivent :
1. cesser de recevoir de nouveaux travaux quand nécessaire;
2. traiter ou réassigner les requêtes en cours selon protocole;
3. fermer les sockets et connexions;
4. écrire durablement les états/acquittements nécessaires;
5. terminer avant le délai.

Les PDB encadrent certaines évictions volontaires, pas toutes les interruptions. Le kubelet peut également évincer sous pression disque/mémoire, avec des mécanismes de sélection et de QoS.

## 9. Diagnostic read-only

~~~bash
oc -n NAMESPACE get pod POD -o wide
oc -n NAMESPACE describe pod POD
oc -n NAMESPACE get pod POD -o jsonpath='{.status.containerStatuses[*].state}{"\n"}'
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc get nodes -o wide
oc adm top pods -n NAMESPACE --containers
~~~

L'affichage des logs n'est pas automatiquement sans risque de confidentialité; des applications peuvent loguer des tokens et des données client. Lire uniquement avec autorisation et conserver les preuves sous forme expurgée.

### Tableau de discrimination

| Symptôme | Plan prioritaire | Autres hypothèses |
|---|---|---|
| Pod Pending sans nodeName | scheduler | quotas/admission en amont |
| ContainerCreating long | mounts, CNI, runtime | image, nœud, CSI |
| ImagePullBackOff | image/registry | DNS, CA, authN |
| CrashLoopBackOff | process/probes/config | permissions, OOM |
| OOMKilled | mémoire/cgroup | limite, fuite, pic légitime |
| Running non Ready | readiness/probes/dépendances | port, policy, app |
| Pod Terminating long | hooks/finalizers/I/O | kubelet, storage |

## 10. Étude banque/EDA

Un consumer de file MQ doit garantir un comportement défini à l'arrêt d'un Pod :
- stop de la lecture de nouveaux messages;
- délai de grâce compatible avec les traitements actifs;
- acknowledgement uniquement après réussite de l'étape prévue;
- stratégie de redelivery et idempotence côté métier;
- monitoring des messages « in flight »;
- séparation entre scaling Kubernetes et capacité MQ/DB.

Trois replicas d'un consumer n'offrent pas automatiquement exactly-once, pas plus que l'affichage Pod Ready. Les contrats du broker et du traitement métier gouvernent les garanties.

## 11. Questions de revue

1. Différence entre kubelet, CRI-O et runtime OCI bas niveau ?
2. Pourquoi un container peut-il être Running mais not Ready ?
3. Pourquoi CrashLoopBackOff n'est-il pas un problème scheduler ?
4. Comment distinguer un refus SCC d'une permission filesystem runtime ?
5. Quelles métriques vérifier en présence de CPU throttling ?
6. Comment garantir un arrêt acceptable d'un MQ consumer ?
7. Un Pod qui redémarre sans erreur garantit-il zéro perte de données ?

## Sources

- [Kubernetes — Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Kubernetes — Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Kubernetes — Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Red Hat — OpenShift 4.22 Architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — Machine configuration](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_configuration/machine-config-index)

**Statut :** étude documentaire. Aucun changement de runtime ou charge sur CRC.


## 12. Vue détaillée du cycle Pod : de l'image au processus

Un objet Pod accepté par l'API n'est pas un processus Linux. Le scheduler lui attribue un nœud; le kubelet du nœud prépare le runtime via CRI-O, qui s'appuie sur un runtime compatible OCI et les mécanismes du noyau Linux.

Les erreurs changent de nature au fur et à mesure :

| Étape | Signal observable | Domaine d'enquête |
|---|---|---|
| Création Pod refusée | Forbidden / admission denied | RBAC, SCC, PSA, quota, webhook |
| Non assigné | Pending / FailedScheduling | Scheduler, topology, requests, PVC |
| Téléchargement image | ErrImagePull / ImagePullBackOff | Registry, digest, CA, pull secrets |
| Création processus | CreateContainerError | UID, permissions, runtime, mounts |
| Process lancé puis terminé | CrashLoopBackOff | Exit code, logs, liveness, OOM |
| Process actif non prêt | Running, Ready=False | Readiness, endpoints, dépendances |
| Process se termine | Terminating | Hooks, volumes, shutdown, finalizers |

Les Codes Ready/Running ne prouvent pas le succès métier. La séparation des étapes évite d'effectuer des « redémarrages d'essai » qui détruisent l'état disponible pour le diagnostic.

## 13. Arrêt gracieux d'un consommateur MQ

Scénario pédagogique : un Pod traite un message bancaire puis émet un acknowledgement à un broker.

À la réception d'une terminaison volontaire :
1. cesser de demander de nouveaux messages;
2. relever les messages en vol et leur statut;
3. terminer les opérations engagées ou les rendre rejouables;
4. n'émettre l'ack que dans les conditions fixées par le contrat de transaction;
5. fermer proprement connexions et ressources;
6. terminer dans le délai de grâce alloué.

Une perte de connexion après traitement mais avant l'ack peut provoquer une redelivery. Kubernetes ne fournit aucune garantie « exactly once » de la transaction externe. L'application doit utiliser un identifiant stable/idempotent et définir précisément les conséquences des retries.

### 13.1 Probe et interruption

Probes illustratives :

~~~yaml
startupProbe:
  httpGet: {path: /startup, port: 8080}
  failureThreshold: 30
  periodSeconds: 2
readinessProbe:
  httpGet: {path: /ready, port: 8080}
  periodSeconds: 5
  timeoutSeconds: 2
livenessProbe:
  httpGet: {path: /alive, port: 8080}
  periodSeconds: 15
  failureThreshold: 3
~~~

Ce fragment se place au niveau des conteneurs d'un PodSpec et suppose des endpoints réellement implémentés. Il n'est pas un manifeste applicable seul. La liveness doit répondre à la question de la **capacité du processus à progresser**, pas redémarrer chaque Pod au premier timeout du broker.

## 14. CPU throttling versus mémoire OOM

Exercice fictif :

- request CPU : 200m, limit : 300m;
- pic nécessaire pendant une fenêtre : 600m;
- mémoire request : 128Mi, limit : 256Mi;
- pic de mémoire du processus : 310Mi.

Le CPU peut être throttlé lorsque le processus dépasse son quota, et les temps de réponse augmenter alors que le nœud semble libre. Pour la mémoire, dépasser la limite peut produire une terminaison OOMKilled. Ce sont deux mécanismes différents.

La classe QoS Guaranteed nécessite notamment des requests CPU et mémoire égales aux limits correspondantes pour **tous les conteneurs du Pod**. Une QoS Guaranteed n'est pas une assurance contre un incident matériel ou une mauvaise application.

### 14.1 Filesystem read-only et images compatibles UID arbitraire

Une image conforme à une politique de moindre privilège évite de dépendre de root et écrit ses données transitoires dans des volumes appropriés. Si readOnlyRootFilesystem est activé, un chemin en écriture explicite (par exemple un emptyDir borné pour du cache temporaire) peut être nécessaire.

Un emptyDir est éphémère. Le réutiliser pour des données bancaires persistantes constitue une erreur de durabilité. La persistance/backup doit être conçue sur un système adapté, indépendamment du container filesystem.

## 15. Preuve d'incident runtime

Documenter :
- date/version et digest de l'image;
- Node/POD/UID et état des containers;
- reason/exitCode/lastState (si disponible);
- requests, limits et QoS;
- conditions/probes et durée depuis le dernier restart;
- statut du volume/PVC et du réseau;
- métriques de throttling, mémoire et dépendances;
- logs applicatifs anonymisés.

Un rapport de support publiable doit retirer les tokens, données clients et URI internes.

## Références complémentaires

- [Kubernetes — Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Kubernetes — Quality of Service](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Kubernetes — Container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [Kubernetes — Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
