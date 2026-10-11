# 03 — Scheduler, controller-manager, Leases et contrôle de convergence

**Volume 02 · Édition de travail · OpenShift 4.22 / Kubernetes 1.35**  
**Évidence : DOCUMENTATION_OFFICIELLE ; aucun test runtime nouveau.**

## 1. Pourquoi distinguer deux boucles ?

Le kube-scheduler décide **où** un Pod non assigné peut s'exécuter. Le kube-controller-manager héberge plusieurs contrôleurs qui cherchent **combien**, **quelles ressources** ou **quels statuts** devraient exister. Le kubelet du nœud exécute ensuite ce qui a été assigné. Confondre ces responsabilités conduit à rechercher une erreur ImagePullBackOff dans le scheduler ou une erreur FailedScheduling dans CRI-O.

La séquence logique d'un Deployment est :

~~~mermaid
flowchart TD
  D[Deployment spec.replicas=3] --> DC[Deployment controller]
  DC --> RS[ReplicaSet]
  RS --> RC[ReplicaSet controller]
  RC --> P[Pods sans nodeName]
  P --> S[kube-scheduler]
  S --> B[Binding sur noeud éligible]
  B --> K[kubelet / CRI-O]
  K --> ST[Pod status / readiness]
~~~

Chaque lien représente une observation ou une écriture d'API, pas un appel synchrone garanti. Le scheduler ne garantit pas qu'un container démarrera correctement, et un ReplicaSet n'est pas une stratégie de haute disponibilité sans domains de panne.

## 2. Le scheduler filtre avant de classer

La procédure de scheduling utilise un framework de plugins et plusieurs points d'extension. Pour raisonner en architecture, distinguer :

1. **Contraintes non négociables** : ressources demandées, node selector requis, affinities requises, taints non tolérés, topology, conditions de volume.
2. **Préférences et scoring** : critères de préférence, répartition et plugins de score actifs.
3. **Bind** : attribution effective du Pod au nœud.
4. **Mise en œuvre** : kubelet et runtime local.

Les détails précis des plugins et poids dépendent de la configuration et de la version; ne pas transformer cet ordre pédagogique en journal d'exécution garanti.

### Exemple de calcul

Deux nœuds fictifs :

| Nœud | CPU allocatable | CPU déjà demandé | CPU non demandé |
|---|---:|---:|---:|
| A | 4 | 3,4 | 0,6 |
| B | 8 | 5,0 | 3,0 |

Un Pod demande **1000m CPU**. Pour ce critère uniquement, A ne peut pas accueillir 1 CPU de request alors que B le peut. Un usage instantané de 15 % sur A ne change pas la logique du scheduler : la comparaison de base s'effectue sur les requests déjà engagées, non sur le CPU libre mesuré en temps réel.

Mais B peut être rejeté à cause d'un taint, d'un node selector ou d'un volume zonal. Une condition satisfaite n'équivaut jamais à un placement garanti.

## 3. Affinity, tolerations et topologySpread

Ces primitives répondent à des questions différentes :

- **Node selector / node affinity** : sur quels nœuds l'application est-elle admissible ou préférée ?
- **Pod affinity/anti-affinity** : quel rapprochement ou éloignement avec d'autres Pods est souhaité ?
- **Taints/tolerations** : quel workload accepte un nœud que l'on souhaite protéger de Pods génériques ?
- **topologySpreadConstraints** : comment borner la concentration de Pods entre domaines de topology ?

Une toleration ne force pas le placement sur un nœud : elle supprime seulement un obstacle posé par un taint. Une préférence d'anti-affinity n'est pas une contrainte dure. Une contrainte dure de répartition peut empêcher tout Pod de démarrer s'il n'existe pas assez de domaines éligibles.

### Exemple de politique pédagogique

~~~yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: account-reader
~~~

Ce fragment est **incomplet** et non déployable seul. Dans une topologie à une seule zone (notamment CRC mono-nœud), il ne prouve aucune dispersion inter-zones. Des options telles que minDomains et node affinity influencent l'effet réel selon les versions et la configuration.

## 4. Scheduling, storage et admission

Un PVC peut rester Pending sous une StorageClass WaitForFirstConsumer en attendant un consommateur schedulable. Un volume déjà lié peut contraindre le nœud ou la zone d'exécution. Les notions de capacité CPU/RAM et de compatibilité CSI doivent être examinées conjointement.

Un Pod rejeté par RBAC/SCC/PSA ou quota peut ne **jamais être créé** : l'incident se situe avant que le scheduler puisse examiner ce Pod. Le triage doit distinguer un refus de création d'un Pod déjà existant mais Pending.

## 5. Controller-manager et gestion de l'état

Le kube-controller-manager est responsable de boucles de contrôleurs fondamentales. On rencontre notamment les contrôleurs liés aux nœuds, namespaces, service accounts, ReplicaSets, Deployments et endpoints selon les composants/versions concernés.

Une propriété d'exploitation majeure : les contrôleurs visent une **convergence éventuelle**. Ils ne garantissent pas qu'une intention puisse être réalisée lorsque le quota est plein, qu'un objet nécessaire est absent ou que l'API est indisponible.

Exemple : un Deployment vise trois replicas. Un contrôle établit que seuls deux Pods satisfont le sélecteur. Il peut demander un troisième Pod; le scheduler peut ensuite échouer à le placer. Le Deployment controller n'ajoute pas de RAM physique au cluster.

### OwnerReferences et finalizers

- ownerReferences indiquent les relations de propriété dans l'API, utilisées notamment par le garbage collector.
- finalizers demandent un traitement préalable à la disparition de l'objet.

Une ressource bloquée sur deletionTimestamp ne doit pas automatiquement voir ses finalizers supprimés : cela peut court-circuiter le nettoyage d'un stockage, d'un compte externe ou d'une ressource réseau.

## 6. Contrôleurs répliqués et Lease

En configuration HA, scheduler et controller-manager peuvent disposer de plusieurs instances; la **leader election** via Lease évite que plusieurs instances effectuent simultanément des opérations censées être uniques. Un Lease peut contenir une identité de holder et des informations de durée/renouvellement.

Limites :
- le mécanisme organise les instances du contrôleur, pas les transactions de l'application;
- un basculement de leader peut créer des délais de convergence;
- un ancien leader qui a émis une requête vers un service externe peut avoir laissé un effet avant de perdre son Lease;
- les systèmes non transactionnels nécessitent une gestion spécifique de l'idempotence.

Ne pas déduire de deux replicas du scheduler qu'il y a deux schedulers actifs qui placent chacun la moitié des Pods.

## 7. Diagnostic read-only d'un Pod Pending

~~~bash
oc -n NAMESPACE get pod POD -o wide
oc -n NAMESPACE describe pod POD
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc get nodes -o wide
oc describe node NODE
oc -n NAMESPACE get resourcequota,limitrange,pvc
~~~

Cette séquence se déroule seulement dans un environnement autorisé et peut exposer des métadonnées internes; expurger les sorties avant publication.

| Message | Question discriminante |
|---|---|
| Insufficient cpu / memory | Sum(requests) vs allocatable et autres réservations ? |
| Untolerated taint | Tolérance voulue ou nœud non prévu ? |
| Volume node affinity conflict | PVC/PV lié à une zone incompatible ? |
| Node affinity mismatch | Label requis absent ? |
| Too many pods | Capacité Pods du nœud ou admission ? |

Un \`oc adm top nodes\` complète le diagnostic mais ne remplace pas le tableau des ressources allouées du nœud.

## 8. Incident N3 : maintenance, PDB et blocage de drain

Une maintenance demandant la sortie de Pods d'un nœud doit respecter les règles de disruption et les capacités restantes. Un PodDisruptionBudget limite certaines évictions volontaires, mais **ne constitue pas une garantie** face à une panne physique.

Scénario :
- un Deployment possède deux replicas;
- une politique PDB exige minAvailable=2;
- les deux réplicas sont disponibles sur deux nœuds;
- une maintenance veut drainer un nœud.

Selon le nombre de replicas disponibles et la capacité du cluster, le PDB peut bloquer l'éviction. La « correction » n'est pas immédiatement de supprimer le PDB. Il faut examiner la marge de capacité, la stratégie rollout/maintenance et le niveau de risque accepté.

## 9. Questions d'architecte

1. En quoi \`scheduler\` et \`kubelet\` diffèrent-ils ?
2. Pourquoi Pending ne signifie-t-il pas automatiquement « manque CPU » ?
3. Que signifie une toleration si le Pod n'a aucune node affinity ?
4. Comment prouver la dispersion dans plusieurs zones ?
5. Quelle est la limite de la leader election pour des side effects externes ?
6. Quelle différence entre resourceVersion, generation et observedGeneration ?
7. Pourquoi ne faut-il pas supprimer les finalizers d'une ressource sans connaître leur propriétaire ?

## Sources

- [Kubernetes — Scheduling](https://kubernetes.io/docs/concepts/scheduling-eviction/)
- [Kubernetes — Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Kubernetes — Topology spread constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Kubernetes — Leases](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Red Hat OCP 4.22 — Cluster Operators reference](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operator-reference)

**Reste à valider :** configuration effective du scheduler et tests de placement sur une topologie multinœud autorisée.
