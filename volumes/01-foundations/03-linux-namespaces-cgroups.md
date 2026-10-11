# 03 — Linux : processus, namespaces, cgroups et isolation des conteneurs

**Volume 01 · DRAFT · Niveau : ingénierie système → architecture de plateforme**  
**Base technique : Linux / cgroup v2 ; application OpenShift 4.22**  
**Preuve : PUBLIC_VERIFIED (documents officiels) ; aucun test runtime réalisé dans cette itération.**

## Objectifs

Savoir expliquer le rôle du noyau dans un conteneur, distinguer isolation et limitation de ressources, diagnostiquer CPU throttling et OOM, comprendre l'apport de SELinux/seccomp, et relier ces mécanismes aux décisions Kubernetes/OpenShift. À la fin, le lecteur doit pouvoir justifier pourquoi « un conteneur n'est pas une machine virtuelle ».

## 1. Un conteneur est un ensemble de processus

Une machine virtuelle comporte normalement un noyau invité exécuté sur un hyperviseur. Un conteneur Linux ordinaire partage le noyau de l'hôte. Les processus s'exécutent avec des vues filtrées de certains objets du système et des quotas/contrôles de ressources. Il ne s'agit pas d'un noyau isolé par défaut.

Les trois mécanismes fondamentaux sont distincts :

| Mécanisme | Répond à la question | Ce qu'il ne fait pas |
|---|---|---|
| Namespace | Quels objets ce processus **voit-il** ? | Ne garantit pas une part de CPU ni un plafond mémoire |
| cgroup | Quelles ressources peut-il **consommer** ou partager ? | Ne cache pas la table des processus ou le réseau |
| Capabilities + LSM + seccomp | Quelles **opérations** lui sont-elles autorisées ? | Ne remplacent pas la segmentation réseau ni le contrôle d'accès API |

Ces mécanismes se combinent avec les droits Unix, les espaces de montage, les règles réseau et le runtime OCI. « Être root dans le conteneur » n'est donc ni automatiquement équivalent à root sur l'hôte, ni automatiquement sans risque. Il faut examiner les user namespaces, les capabilities effectives, les montages, le mode privileged et les accès aux sockets de runtime.

## 2. Les namespaces, un par un

### 2.1 PID : une vue différente des processus

Un processus peut avoir PID 1 à l'intérieur de son namespace PID et un PID différent sur l'hôte. Cela ne crée pas une machine indépendante : la gestion mémoire, l'ordonnanceur CPU et les mécanismes de sécurité restent ceux du noyau hôte.

Le PID 1 du conteneur a un rôle opérationnel particulier : il doit traiter les signaux de terminaison et réaper les processus enfants. Une application incapable de traiter SIGTERM ralentit l'arrêt gracieux d'un Pod et peut finir arrêtée par SIGKILL après sa période de grâce.

**Diagnostic** : les processus zombies ou l'arrêt lent lors d'un rollout peuvent relever du comportement du processus principal, pas du scheduler Kubernetes.

### 2.2 Mount : espaces de montage et propagation

Un mount namespace peut présenter une arborescence de montages différente de celle de l'hôte. Des mounts bind, des volumes Kubernetes et des couches de système de fichiers peuvent coexister.

La couche écrivable du conteneur est en principe éphémère; une modification locale n'est pas une sauvegarde. Un volume persistant constitue une autre frontière avec un cycle de vie et des garanties dépendants du CSI et du stockage. Les options de propagation de montage peuvent avoir des conséquences de sécurité; elles ne doivent pas être activées par défaut.

### 2.3 Network : piles réseau distinctes

Un network namespace possède ses interfaces, adresses IP, routes et tables de ports. Un Pod Kubernetes partage habituellement un namespace réseau entre ses conteneurs : ceux d'un même Pod se contactent via localhost, alors que deux Pods différents disposent normalement de stacks séparées.

Chaîne conceptuelle :

~~~text
Application (socket TCP)
       ↓
Network namespace du Pod (eth0 + routes)
       ↓
Paire veth / interfaces virtuelles / dataplane CNI
       ↓
Réseau du nœud / overlay / réseau physique
       ↓
Service ou destination distante
~~~

La réalisation concrète varie selon le CNI. Dans OpenShift, éviter de supposer que tous les dataplanes sont de simples bridges Linux : OVN-Kubernetes a sa propre architecture, détaillée au Volume 04.

### 2.4 UTS, IPC, user, cgroup, time

- **UTS** : vue du hostname et du nom de domaine NIS.
- **IPC** : espaces de communication interprocessus et certaines ressources associées.
- **User** : correspondance UID/GID entre intérieur et extérieur; l'UID 0 visible dans un user namespace peut correspondre à un UID non privilégié hors de ce namespace.
- **Cgroup namespace** : vue des chemins de contrôle de ressources, pas la ressource elle-même.
- **Time** : possibilité d'isoler certaines horloges, selon noyau et configuration.

**Erreur fréquente** : croire que toutes ces catégories sont nécessairement actives, disponibles et isolées de la même manière pour chaque Pod. C'est la combinaison de la politique de sécurité, du runtime et du noyau qui fait foi.

## 3. cgroups : partitionner les ressources, pas les réserver magiquement

cgroup v2 organise les processus dans une hiérarchie. Les contrôleurs allouent ou limitent des ressources. Deux catégories de valeurs doivent être distinguées :

- **CPU** : la limite se manifeste par du throttling lorsque le quota est consommé; un request Kubernetes influence le placement et la distribution relative, mais ne promet pas qu'une application aura toujours ce débit instantanément.
- **Mémoire** : lorsque la mémoire atteignable dans le groupe est insuffisante et ne peut être récupérée, un OOM kill peut survenir. L'usage mémoire n'est pas un débit plafonné : la mémoire n'est pas « ralentie » comme le CPU.

### 3.1 Fichiers courants cgroup v2

| Fichier | Sens opérationnel | Interprétation |
|---|---|---|
| cpu.max | Quota/période | max = pas de plafond via ce mécanisme |
| cpu.weight | Part relative quand il y a contention | Poids, pas vCPU garanti |
| cpu.stat | Usage et throttling | Observer l'évolution des compteurs |
| memory.current | Occupation mesurée | Différente de la mémoire réservée |
| memory.max | Limite supérieure | Peut conduire à OOM |
| memory.events | Événements mémoire | Compteurs high/max/oom/oom_kill |
| pids.current / pids.max | Nombre de tâches et plafond | Une saturation empêche de nouvelles tâches |

Ces fichiers n'apparaissent pas nécessairement à la racine visible d'un container ou d'un hôte Windows. Un Pod peut ne pas avoir accès aux contrôles cgroup du nœud — et c'est souhaitable dans une configuration durcie.

### 3.2 Traduction des ressources dans Kubernetes

Exemple **illustratif, non déployé**, pour un container :

~~~yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi
~~~

- **250m** signifie un quart de CPU dans l'unité Kubernetes; ce n'est pas une réservation d'un cœur physique dédié.
- **256Mi** contribue à la décision de scheduling et au calcul des besoins; ce n'est pas une limite.
- **1 CPU** comme limite fixe un plafond d'utilisation CPU contrôlé par le noyau (selon politiques et implémentation).
- **512Mi** est la limite mémoire; des allocations au-delà du possible peuvent entraîner une terminaison OOM.
- Le scheduler évalue les requests et l'allocatable, **pas** la mémoire libre instantanée seule.
- Les valeurs par défaut peuvent provenir de LimitRange ou d'autres politiques d'admission. Une limite sans request explicite peut entraîner un request égal à cette limite selon le traitement applicable.

### 3.3 Étude quantitative : noeud 8 CPU / 24 Gi allocatables

Supposons 4 Deployments réclamant chacun 2 Pods à 500m/1Gi. La demande totale est :

- CPU demandé = 4 × 2 × 0,5 = **4 CPU**.
- Mémoire demandée = 4 × 2 × 1 Gi = **8 Gi**.

Le fait que la somme tienne dans 8 CPU et 24 Gi ne prouve pas le placement réel : tolérations, affinités, DaemonSets, capacité effective par nœud, ressources déjà demandées et contraintes de stockage comptent aussi. Sur un CRC mono-nœud, une panne du nœud rend toutes ces répliques indisponibles. Répliquer ne transforme donc pas un laboratoire mono-nœud en HA.

## 4. Isolation n'est pas autorisation

### Capabilities

La séparation des privilèges Linux permet d'accorder certains pouvoirs sans donner tous les pouvoirs. Ajouter CAP_SYS_ADMIN pour résoudre un problème de montage élargit considérablement la surface de risque. Préférer la suppression des capabilities inutiles.

### seccomp

seccomp réduit les appels système autorisés pour le processus. Le profil **RuntimeDefault** limite normalement davantage qu'Unconfined, mais doit être testé avec le workload réel. Il ne prouve pas qu'une application est exempte de vulnérabilités.

### SELinux

SELinux met en œuvre des règles de contrôle d'accès obligatoires liées à des étiquettes et à des politiques. Un échec de lecture/écriture malgré un chmod permissif peut venir d'une décision SELinux. Sous OpenShift, ne pas « corriger » par l'ouverture globale des privilèges ou la désactivation de SELinux : rechercher la cause et la configuration supportée.

### Security Context Constraints (SCC)

Les SCC d'OpenShift contrôlent, à l'admission, des capacités comme les UID, les host paths, le mode privilégié ou les capabilities. Un Pod qui exige un UID particulier peut ne pas être admissible avec les SCC accordées au service account. L'architecture d'une image compatible avec des UID arbitraires réduit ce problème. Les particularités des user namespaces et des SCC évoluent selon les versions.

## 5. Chaîne d'exécution : d'un Pod au noyau

~~~mermaid
flowchart LR
  API[PodSpec dans l'API] --> K[kubelet du nœud]
  K --> CRI[CRI : CRI-O]
  CRI --> OCI[Runtime OCI bas niveau]
  OCI --> N[Namespaces et montages]
  OCI --> CG[cgroups CPU / mémoire / PID]
  OCI --> SEC[SELinux / seccomp / capabilities]
  N --> P[Processus Linux]
  CG --> P
  SEC --> P
~~~

Sur OpenShift 4.22, RHCOS intègre kubelet et CRI-O; le runtime OCI bas niveau peut être crun ou runc selon configuration. **Ne pas confondre Dockerfile, image OCI, CRI-O et runtime OCI** : ce sont des niveaux différents du pipeline.

## 6. Diagnostic raisonné

| Symptôme | Hypothèses | Observations non destructives | Mauvaise réponse |
|---|---|---|---|
| Pod OOMKilled | Limite trop basse, fuite, pic de charge | oc describe pod, events, métriques mémoire | Monter la limite sans mesure |
| Latence avec CPU non saturé globalement | Throttling local du cgroup, contention | metrics throttling, requests/limits, charge applicative | Se fier seulement au CPU moyen du nœud |
| Permission denied sur volume | UID/GID, SCC, SELinux, FSGroup, mode de montage | PodSpec, événements, permissions applicatives, labels si accès autorisé | privileged=true |
| Pod bloqué Terminating | Processus PID 1 ignorant SIGTERM, finalizer, I/O | oc describe, logs, état des contrôleurs | Force delete immédiat |
| Connexion entre Pods échoue | DNS, policy, route, service/endpoints, socket | oc get svc/endpointslices/networkpolicies, logs | Ouvrir tout l'egress |

Le diagnostic commence par la **propriété violée** (capacité, isolement, privilège, réseau, stockage), pas par la commande qui relance l'application.

## 7. Atelier Linux local, sans modification

Sur un hôte Linux (pas sur Git Bash Windows natif) :

~~~bash
uname -sr
id
cat /proc/self/cgroup
ls -l /proc/self/ns
test -e /sys/fs/cgroup/cgroup.controllers && cat /sys/fs/cgroup/cgroup.controllers
test -e /sys/fs/cgroup/memory.max && cat /sys/fs/cgroup/memory.max
~~~

Pour comparer des processus, lire par exemple `/proc/1/ns` et `/proc/self/ns` si les droits le permettent. Les identifiants d'objets namespace peuvent varier; **ne pas en déduire qu'un conteneur utilise une technologie donnée** sans vérifier son contexte d'exécution.

Les commandes ci-dessus sont de la lecture. Ne pas lancer `unshare`, ne pas modifier les fichiers cgroup et ne pas obtenir une session privilégiée sur un nœud de cluster pour un simple exercice.

## 8. Questions d'architecte — réponses attendues

1. **Pourquoi un conteneur n'est-il pas une VM ?** Il partage ordinairement le noyau hôte; une VM dispose d'un noyau invité et d'une isolation par hyperviseur.
2. **Est-ce qu'une limite CPU de 1 signifie un cœur dédié ?** Non : elle plafonne la consommation CPU selon le mécanisme de quota; le placement et la contention restent à analyser.
3. **Pourquoi un Pod peut-il subir OOMKilled sur un nœud doté de mémoire libre ?** Une limite mémoire locale peut être dépassée indépendamment de la mémoire globale du nœud.
4. **Faut-il fixer runAsUser=1000 partout ?** Non : les politiques SCC et images adaptées aux UID arbitraires doivent guider le choix; figer un UID peut être incompatible avec l'admission.
5. **Comment valider l'isolation ?** Par politiques d'admission, vérification des privilèges, des montages, du réseau, de la segmentation et par des tests de frontières, pas par la seule présence d'un container.

## Références primaires et limitations

- [Linux namespaces (man-pages)](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Linux kernel — cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [Kubernetes — Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes — Kernel security constraints](https://kubernetes.io/docs/concepts/security/linux-kernel-security-constraints/)
- [Red Hat — OCP 4.22 architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — OCP 4.22 Working with pods / user namespaces](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/nodes/working-with-pods)

**Étape de validation restante :** confronter les exemples cgroup et SCC à un environnement OpenShift autorisé; ne pas confondre la documentation avec une preuve de lab.
