# 11 — Machine API : Machines, MachineSets, autoscaling et santé des nœuds

**Volume 02 · ÉDITION 1.2 — RELECTURE DOCUMENTAIRE · OCP 4.22 · PUBLIC_VERIFIED pour les concepts documentés.**  
**Aucune création/suppression de Machine, aucune intervention sur le CRC.**

## 1. Une Machine n'est pas un Node, un MachineSet n'est pas un MCP

Dans une architecture OpenShift installée sur une infrastructure compatible avec la gestion des Machines, la Machine API représente des **machines de l'infrastructure** et automatise une partie du provisionnement après installation.

Le système distingue :
- l'instance d'infrastructure (VM, hôte, instance cloud selon provider);
- l'objet **Machine**, qui décrit le cycle de vie d'un hôte et peut être lié à un Node Kubernetes ;
- le **Node**, qui représente un agent kubelet enregistré auprès de Kubernetes ;
- le **MachineSet**, qui contrôle le nombre de Machines de calcul demandées ;
- le **MachineConfigPool**, qui contrôle la convergence de la configuration OS pour un groupe de nœuds ;
- les ressources **MachineHealthCheck**, **MachineAutoscaler**, **ClusterAutoscaler** ;
- le **ControlPlaneMachineSet** sur les plateformes et configurations prises en charge.

La Machine API et le MCO pilotent donc deux dimensions **orthogonales** : *avoir une machine* versus *configurer la machine*. La confusion entraîne des opérations dangereuses telles que « scale le MachineSet pour corriger un MCP Degraded », sans comprendre le changement de capacity ou les données.

~~~mermaid
flowchart LR
  MS[Compute MachineSet] --> MA[Machines désirées]
  MA --> INFRA[Provider infrastructure]
  INFRA --> NODE[Kubernetes Nodes]
  NODE --> MCP[MachineConfigPool]
  MCP --> MCO[MCO / rendered MachineConfig]
  CA[ClusterAutoscaler] --> MAS[MachineAutoscaler]
  MAS --> MS
  MHC[MachineHealthCheck] --> MA
~~~

**Attention** : le dessin est une carte de responsabilités, pas une représentation exhaustive des reconcile loops. Les ressources de l'API Machine varient selon la plateforme; certains clusters UPI n'ont pas de MachineSets de workers gérés.

## 2. Propriétés et dépendances d'une Machine

Une ressource Machine contient des informations propres au fournisseur sous la forme d'une configuration provider. L'état de la Machine peut précéder celui d'un Node Kubernetes : la VM peut exister alors que son démarrage, son bootstrap ou l'enregistrement kubelet sont encore incomplets.

| Objet | Cycle de vie | Contrat d'observation |
|---|---|---|
| Machine | Hôte déclaré/observé par Machine API | Phase, provider status, relation au Node |
| Node | Agent Kubernetes enregistré | Conditions Ready/Pressure, allocatable, pods |
| MachineSet | Replicas de Machines de compute désirés | Ready/available replicas et conditions |
| MachineConfigPool | Configuration système des Nodes d'un pool | Updated, Updating, Degraded |
| Deployment | Replicas de Pods d'une application | Available, Progressing |
| PVC | Demande de volume persistant | Bound, Pending, classe et topology |

Une Machine créée ne prouve pas que le Node est Ready. Un Node Ready ne prouve pas que l'application dispose d'une capacité libre suffisante, ni que tous les volumes pourront se monter.

### 2.1 MachineSet est au Machine ce que ReplicaSet est au Pod — jusqu'à une certaine limite

La comparaison est utile pour expliquer les replicas désirés. Cependant, la création/suppression de Machines peut produire des opérations sur des VM, IP, disques, services cloud et coûts. Elle peut aussi provoquer des évictions et des changements de topology. Il faut donc éviter de traiter \`spec.replicas\` d'un MachineSet comme une valeur sans conséquence : **ce n'est pas un exercice à exécuter sur le CRC**.

## 3. Compatibilité IPI/UPI : ne jamais supposer les ressources présentes

La Machine API offre une gestion automatisée avancée sur des plateformes prises en charge. Pour des installations entièrement UPI et certaines variantes de cluster, la gestion d'infrastructure peut être externe ou partiellement disponible.

Avant un design :
1. consulter le type de plateforme de l'installation;
2. vérifier que la Machine API est opérationnelle ;
3. inventorier les MachineSets et Machines effectivement présents ;
4. vérifier le support de MachineAutoscaler et de MachineHealthCheck ;
5. identifier quel composant/équipe crée les hôtes lorsque Machine API n'est pas l'autorité ;
6. consulter la **documentation OCP 4.22 propre au provider**.

Un namespace \`openshift-machine-api\` présent ne suffit pas, à lui seul, à garantir que chaque Machine créée pourra allouer une nouvelle VM.

## 4. Autoscaling : trois boucles différentes

### 4.1 HorizontalPodAutoscaler : des Pods, pas des VM

Le HPA vise le nombre de Pods d'un workload selon ses métriques et politiques. Si le scheduler ne trouve plus de nœud éligible, ajouter des Pods désirés peut augmenter le backlog Pending sans créer de nouveau Node.

### 4.2 ClusterAutoscaler : une décision de capacité cluster

Dans les déploiements OCP 4.22 compatibles, ClusterAutoscaler évalue les Pods non schedulables et les ressources disponibles, selon le contrat de configuration. Ses limites portent notamment sur le nombre maximal de Nodes et des budgets CPU/RAM/GPU.

Le ClusterAutoscaler **ne remplace pas** l'API d'infrastructure ni le besoin de MachineAutoscalers associés aux MachineSets.

### 4.3 MachineAutoscaler : bornes par MachineSet

Pour permettre l'ajustement du nombre de Machines d'un compute MachineSet, Red Hat documente une ressource MachineAutoscaler associée à chaque MachineSet visé. **Un ClusterAutoscaler sans MachineAutoscaler ne déploie pas de nouvelles Machines par ce mécanisme.**

Exemple documentaire (à ne pas appliquer) :

~~~yaml
apiVersion: autoscaling.openshift.io/v1beta1
kind: MachineAutoscaler
metadata:
  name: worker-zone-a
  namespace: openshift-machine-api
spec:
  minReplicas: 1
  maxReplicas: 4
  scaleTargetRef:
    apiVersion: machine.openshift.io/v1beta1
    kind: MachineSet
    name: worker-zone-a
~~~

Le MachineSet nommé n'existe pas nécessairement; les bornes et le support du scale-to-zero dépendent du provider. En particulier Red Hat 4.22 impose des réserves sur \`minReplicas: 0\` et sur certains MachineSets installés par IPI; consulter le guide avant une décision de coût.

### 4.4 Machine API versus Kubernetes Cluster API

Des ressources OpenShift Machine API historiques coexistent avec les mécanismes liés au **Cluster API** dans la documentation 4.22. Certaines fonctionnalités de migration et de gestion via Cluster API sont signalées comme *Technology Preview* : elles ne doivent **pas** être assimilées aux mêmes SLA et recommandations qu'une fonctionnalité GA. Documenter l'API exacte et son statut de support dans chaque ADR.

## 5. MachineHealthCheck : automatisation de remédiation, pas restauration de données

La MachineHealthCheck (MHC) détecte des Machines jugées malsaines selon des critères configurés et peut déclencher leur remplacement sur des plateformes supportées. Le mécanisme ajoute un risque : une panne partagée de DNS, storage ou réseau peut faire apparaître plusieurs Nodes malades simultanément.

Questions indispensables :
- quelle définition d'un Node défaillant et quelle fenêtre d'observation ?
- quel plafond de Machines peuvent subir une remédiation simultanée ?
- quels workloads stateful et volumes sont impactés ?
- quelles contraintes de quorum etcd et de placement s'appliquent ?
- le provider sait-il **réellement** recréer une Machine ?
- comment l'alerte se comporte-t-elle pendant une maintenance volontaire ?

Une MHC n'est ni un backup, ni un plan de PRA, ni une preuve de zéro interruption.

## 6. ControlPlaneMachineSet : rôle distinct

Les compute MachineSets ne gèrent pas les nœuds control plane. Sur certains providers compatibles, le **ControlPlaneMachineSet** permet une gestion déclarative des machines du plan de contrôle selon des modalités spécifiques à OCP.

Ce point exige davantage de prudence qu'un MachineSet worker : une mauvaise modification peut perturber le quorum, le load balancer API ou les domaines de panne. Toute opération de modification, migration ou remplacement doit être supportée par la version et le provider, avec backup etcd conforme et procédure approuvée.

## 7. Observation en lecture seule

~~~bash
oc get infrastructure cluster -o yaml
oc get clusteroperator machine-api
oc -n openshift-machine-api get machines.machine.openshift.io
oc -n openshift-machine-api get machinesets.machine.openshift.io
oc -n openshift-machine-api get machinehealthchecks.machine.openshift.io
oc -n openshift-machine-api get machineautoscalers.autoscaling.openshift.io
oc get clusterautoscalers.autoscaling.openshift.io
oc get nodes -o wide
oc get machineconfigpools
~~~

Sur certains clusters, une ressource peut ne pas exister ou ne pas être listable avec les droits du lecteur. Cela doit être consigné comme **visibilité ou support à confirmer**, pas assimilé à une panne. Les commandes ne doivent pas être exécutées sur des clusters non autorisés; la collecte peut exposer des métadonnées d'infrastructure.

### 7.1 Matrice de diagnostic N3

| Observation | Frontière plausible | Vérification suivante |
|---|---|---|
| Machines voulues, aucune nouvelle Machine créée | MachineSet/contrôleur/provider/quota cloud | Conditions MachineSet, provider errors |
| Machine existe, Node absent | Bootstrap, OS, réseau, kubelet | Machine phase, events et fournisseur |
| Node Ready mais MCP Degraded | Configuration système MCO | Rendered config et MachineConfigPool |
| Pods Pending, CA non scalable | Autoscaler, maxNodes, bound des MachineAutoscalers | Conditions et requests des Pods |
| MachineHealthCheck remplace plusieurs workers | Défaillance commune ou seuils trop agressifs | Plafonds, topology, dépendances |
| Machine supprimée et volume non réattachable | CSI/topology/données | PV/PVC, storage et RPO/RTO |

## 8. Incident illustratif : « HPA augmente, aucun nouveau Pod Ready »

Les replicas désirés passent de 6 à 12. Les six nouveaux Pods sont Pending avec FailedScheduling, \`Insufficient cpu\`. Le système ne possède pas de capacité libre suffisante.

Hypothèses :
1. HPA a évolué correctement, mais les Nodes sont saturés en *requests*.
2. Le ClusterAutoscaler est absent ou désactivé.
3. Aucun MachineAutoscaler ne cible le MachineSet approprié.
4. Le MachineSet a atteint sa borne maxReplicas.
5. Le provider refuse de créer une instance (quota/cloud API).
6. Un nouveau Node est provisionné, mais son MCO/bootstrap échoue.
7. Les Pods portent un selector/taint/volume empêchant de profiter des nouveaux nœuds.

**Corrigé :** examiner les Events du scheduler puis la chaîne HPA → ClusterAutoscaler → MachineAutoscaler → MachineSet → Machine → Node, avec des observations à chaque frontière. Augmenter le HPA sans lever le blocage de capacité peut accroître la file Pending sans améliorer les transactions.

## 9. ADR : cluster de banque avec capacité GPU saisonnière

**Besoin :** ajouter ponctuellement des Machines GPU pour des traitements d'IA, avec plafond de coût, sans affecter la disponibilité des APIs bancaires. Un MachineSet de compute spécialisé et un MachineAutoscaler peuvent faire partie du design si le provider et l'architecture OCP les supportent.

Décisions à rendre explicites :
- dimensionnements CPU, RAM, GPU, quota provider et prix/heure;
- séparation des workloads GPU et des APIs critiques;
- limites de scale-to-zero selon le provider;
- tolérance au temps d'acquisition d'une Machine et de pull d'images;
- isolation de réseau et sécurité de l'infrastructure;
- récupération d'un Node GPU et absence de données persistantes locales;
- mesure SLI de l'application et enveloppe carbone/énergétique.

Aucun coût chiffré n'est inventé sans provider, région et mesure des GPU réellement choisis.

## 10. Questions d'évaluation

1. Quelle différence entre un Machine et un Node ?
2. Pourquoi le MCO ne remplace-t-il pas la Machine API ?
3. Quand MachineSet=3 ne signifie-t-il pas « 3 Nodes Ready » ?
4. Pourquoi un ClusterAutoscaler peut-il ne créer aucun Node malgré des Pods Pending ?
5. Comment démontrer qu'un cluster UPI supporte les Machines déclaratives ?
6. MachineHealthCheck est-il un backup ?
7. Quelle différence entre ControlPlaneMachineSet et compute MachineSet ?
8. Pourquoi le support du Cluster API doit-il être vérifié par feature/version ?

## Références officielles

- [Red Hat OCP 4.22 — Machine management](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/index)
- [Red Hat OCP 4.22 — Autoscaling](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/applying-autoscaling)
- [Kubernetes — Node](https://kubernetes.io/docs/concepts/architecture/nodes/)
- [Kubernetes — HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

**Statut :** chapitre de référence, sans création, remplacement ni suppression d'une Machine.


## 11. Conditions nécessaires au scale-out Machine API

Le diagnostic d'un HPA qui augmente les replicas sans obtenir de nouveaux Pods Ready ne doit pas conclure que « le ClusterAutoscaler est en panne » avant de montrer la chaîne :

~~~text
HPA souhaite +replicas Pods
     |
     v
Pods réellement Pending et non schedulables ?
     |
     +-- non : autres contraintes d'admission, readiness ou runtime
     |
     +-- oui : ClusterAutoscaler actif et non bloqué ?
                  |
                  v
               MachineAutoscaler ciblant un MachineSet ?
                  |
                  v
               Bornes min/max, provider quota et policy scale ?
                  |
                  v
               Machine créée -> Node rejoint le cluster ?
                  |
                  v
               MCO/kubelet convergés -> Pod schedulable/Ready ?
~~~

Avoir \`MachineAutoscaler.maxReplicas > replicas actuel\` n'est pas une preuve de capacité disponible : le provider peut refuser une VM, les quotas peuvent empêcher le lancement, un volume zonal peut limiter le placement, ou des labels et taints exclure le nouveau Node.

### 11.1 Permissions et ownership

L'équipe applicative règle les replicas HPA et la définition de requests de ses Pods dans les budgets approuvés. L'équipe Platform Engineering possède la configuration ClusterAutoscaler/MachineAutoscaler, et l'Infrastructure gère quotas, pools cloud et topologie.

Ces frontières doivent être matérialisées dans RBAC/GitOps. Donner à une équipe produit le pouvoir de scaler sans limite des Machines cloud peut avoir un coût financier et énergétique important, et peut saturer des quotas partagés.

### 11.2 Vérification spécifique à la plateforme

Le document Red Hat 4.22 Machine Management indique :
- MachineAutoscaler s'applique aux compute MachineSets ciblés quand ClusterAutoscaler existe ;
- une MachineHealthCheck peut supprimer une Machine malade et déclencher son remplacement sur un provider supporté ;
- la Machine API n'est pas interchangeable avec la gestion MCO de la configuration système ;
- certains modes de gestion via Cluster API et certains chemins de migration sont Technology Preview.

Aucun de ces mécanismes ne doit être supposé disponible sur un cluster UPI, CRC ou autre plateforme sans inventaire et vérification des capacités réellement installées.

[Machine management 4.22 : description et limites](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/index).

## 12. Précision de support — autoscaling et plateformes

La documentation officielle [Machine management 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/applying-autoscaling) indique que le ClusterAutoscaler requiert une **Machine API Operator opérationnelle**. Elle précise que `minReplicas: 0` est applicable à certains providers, notamment AWS, Google Cloud, Azure, RHOSP et vSphere, mais ne doit pas être utilisé pour les trois compute MachineSets initiaux d'une installation IPI. D'autres providers peuvent imposer des restrictions plus fortes.

La formule « scale to zero est possible » sans nommer le provider, la classe de MachineSet et le chemin de support est donc insuffisante. Le chapitre distingue capacités disponibles de configurations autorisées pour l'environnement visé.
