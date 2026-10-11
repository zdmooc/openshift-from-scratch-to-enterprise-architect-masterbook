# V02-L05 — Machine API : diagnostic d'un autoscaling bloqué

**Mode : PAPER_LAB / DOCUMENTED_NOT_RUN. Aucun appel au cloud ni mutation d'un cluster.**  
**Cible : OCP 4.22 sur plateforme disposant de MachineSets de calcul gérés.**

## 1. Mise en situation

Une API de banque est déployée sur OpenShift. Le HPA est passé de 6 à 12 Pods à la suite d'une montée de trafic. Les six nouveaux Pods sont Pending.

Éléments fournis **fictifs** :

| Élément | Observation |
|---|---|
| Pod request | CPU 600m ; mémoire 768Mi |
| Worker-A | allocatable CPU 4 000m, requests engagées 3 800m |
| Worker-B | allocatable CPU 4 000m, requests engagées 3 600m |
| Worker-C | allocatable CPU 4 000m, requests engagées 3 900m |
| MachineSet zone A | replicas désirés 3, replicas Ready 3 |
| MachineAutoscaler zone A | minReplicas=3, maxReplicas=3 |
| ClusterAutoscaler | actif, maxNodesTotal=6 |
| Événement scheduler | 0/3 nodes are available: Insufficient cpu |
| Métrique CPU actuelle | 22 % sur les nœuds |

À la question « Pourquoi les Pods n'ont-ils pas démarré alors que le CPU du cluster semble peu utilisé ? », répondre **avant** de lire le corrigé.

## 2. Exercices

### E1 — Filtre CPU

Pour chaque worker, calculer la différence *allocatable moins requests engagées*.

- A : 4 000 - 3 800 = **200m**.
- B : 4 000 - 3 600 = **400m**.
- C : 4 000 - 3 900 = **100m**.

Aucun worker ne satisfait 600m. Le scheduler ne juge pas ce placement à partir de l'utilisation instantanée de 22 %. Cette valeur peut être exacte et néanmoins non pertinente pour le filtre de requests CPU.

### E2 — Pourquoi le cluster ne grandit pas

Identifier les deux blocages indépendants dans les paramètres fictifs :
- Le MachineAutoscaler du MachineSet a déjà atteint \`maxReplicas=3\`.
- Le ClusterAutoscaler a une limite globale \`maxNodesTotal=6\`, qu'il faut comparer à la taille réelle du cluster. **Le tableau ne précise pas le nombre total de Nodes** : il ne permet pas d'affirmer que cette limite globale est déjà atteinte. Le premier blocage, lui, est établi.

**Corrigé :** le MachineAutoscaler ne peut pas dépasser son maximum déclaré. L'augmentation de maxReplicas ou maxNodesTotal serait une **mutation d'infrastructure** et exige analyse de coûts, quotas et support. On ne la réalise pas dans ce lab.

### E3 — Le modèle de remplacement

Supposons qu'une autorisation de changement ait permis le provisioning d'un nouveau worker avec 4 CPU allocatables. Est-il automatiquement utilisable par les six Pods en attente ? **Non** :

1. Les ressources réelles du provider doivent être disponibles.
2. Machine doit aboutir à Node enregistré.
3. Le Node doit devenir Ready et recevoir sa config MCO.
4. Les taints/labels/PVC/zone doivent accepter le Pod.
5. La capacité mémoire et nombre de Pods doivent être suffisants.
6. Chaque Pod doit démarrer et devenir Ready.

Une Machine créée n'est pas une transaction banque réussie.

### E4 — Machines et Nodes : cause discriminante

Quatre incidents distincts :
- MachineSet veut 4 Machines, seulement 3 existent : examiner contrôleur MachineSet/provider.
- 4 Machines existent mais seulement 3 Nodes : examiner bootstrap, réseau et kubelet.
- 4 Nodes Ready, mais MCP Degraded : examiner rendered config/MCO.
- 4 Nodes Ready et MCP Updated, Pods Pending : examiner scheduling requests/affinity/taints/PVC.

Ne pas remplacer un Node sans preuve de son défaut ni sans plan de sécurité pour les volumes attachés.

## 3. Inventaire autorisé en lecture seule

~~~bash
oc get infrastructure cluster -o yaml
oc get clusteroperator/machine-api
oc -n openshift-machine-api get machinesets
oc -n openshift-machine-api get machines
oc -n openshift-machine-api get machineautoscalers
oc get clusterautoscalers
oc get nodes -o wide
oc get machineconfigpools
~~~

**Ne pas exécuter automatiquement ces commandes sur le CRC**. Elles exigent un contexte autorisé et peuvent exposer la topologie de l'infrastructure.

## 4. ADR de capacité

| Question de décision | Réponse à établir avec preuve |
|---|---|
| Quels types de Machines ? | Capacité réelle, architecture, coûts/heure et énergie |
| Quels quotas du provider ? | CPU/RAM/GPU/instances et disponibilité régionale |
| Quelles zones ? | Domaine de panne et répartition des volumes |
| Peut-on scaler à zéro ? | Vérifier restrictions du provider et des MachineSets d'installation |
| Quelles applications partagent le pool ? | Réservation, PriorityClasses, quotas |
| Quelle politique d'arrêt ? | Scale-down, durée d'attente, interruption et cohérence de données |
| Quel error budget ? | Impact sur SLO pendant temps de provisioning |

## 5. Résultat pédagogique et limite

Ce lab prouve uniquement que le lecteur peut **classifier** un autoscaling bloqué et calculer les contraintes de requests, avec des nombres fictifs. Il ne mesure ni la décision réelle du ClusterAutoscaler, ni la capacité de lancement du provider, ni les économies d'une nouvelle Machine.

Sources : [Red Hat — Applying autoscaling 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/applying-autoscaling) ; [Kubernetes — Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).
