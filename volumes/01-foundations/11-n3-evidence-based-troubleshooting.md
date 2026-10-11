# 11 — Méthode de diagnostic N3 : distinguer incident, symptôme et preuve

**Volume 01 · Statut DRAFT · Cible : Kubernetes / OpenShift 4.22**  
**Preuve : PUBLIC_VERIFIED pour les primitives ; scénarios et simulations = REFERENCE_ARCHITECTURE/OFFLINE_TEST.**

## 1. Objectifs

Savoir mener un triage N3 sans « redémarrer pour voir » : définir le périmètre métier, classer les symptômes par couche, lire l'état désiré et observé, construire des hypothèses falsifiables, rechercher des changements corrélés, mesurer le rétablissement et rédiger un compte rendu qui distingue **cause confirmée**, hypothèse et risque résiduel.

Les volumes ultérieurs détaillent les mécanismes. Celui-ci enseigne **l'ordre de raisonnement**.

## 2. Trois notions qui ne sont pas interchangeables

| Notion | Définition | Exemple |
|---|---|---|
| Symptôme | Ce que l'utilisateur ou le système observe | HTTP 503 depuis une API |
| Observation technique | Mesure ou état relevé à un instant donné | 0 EndpointSlice ready à 11:32 UTC |
| Cause | Mécanisme démontré expliquant les observations | Label du Service ne sélectionne plus le Pod, après changement de manifeste |

Un \`Pod Pending\` est un **état**, pas une cause. \`CrashLoopBackOff\` décrit le comportement de redémarrage du conteneur, pas la raison de son arrêt. \`Degraded=True\` sur un ClusterOperator indique un écart de statut, pas une causalité prouvée avec toutes les erreurs métier.

Éviter les conclusions non supportées, particulièrement « problème réseau » si l'unique preuve est une latence côté client.

## 3. Les huit frontières d'un incident

~~~mermaid
flowchart TD
  A[Impact utilisateur / SLI métier] --> B[DNS externe / LB / Ingress]
  B --> C[Route / Service / EndpointSlices]
  C --> D[NetworkPolicy / dataplane]
  D --> E[Pod / readiness / image]
  E --> F[Scheduler / cgroups / noeud]
  F --> G[Volume / CSI / filesystem]
  G --> H[Dépendances hors cluster et identité]
  H --> I[Version, rollout, politique de déploiement]
~~~

Le diagramme n'est pas un parcours paquet universel : c'est un **ordre de vérification**, à adapter aux indices. Par exemple, si le SLI indique des erreurs strictement liées à l'IdP, il est rationnel de contrôler cette dépendance avant le système de stockage.

### 3.1 Le contrat de triage

Avant toute commande, relever :
- heure de début et fuseau, trafic impacté, nombre de clients et périmètre d'identité;
- version de l'application/digest et dernières modifications GitOps;
- différence entre symptômes externes et internes;
- opérations déjà réalisées;
- éventuelles limites RBAC et absence de certaines données de monitoring.

Ces éléments créent une chronologie et empêchent les faux rapprochements entre incidents.

## 4. Diagnostic du control plane et des nœuds

Commandes non destructives, sous réserve des droits :

~~~bash
oc version
oc get clusterversion
oc get clusteroperators
oc get nodes -o wide
oc get machineconfigpools
oc adm top nodes
~~~

### Comment lire les résultats

- **Node Ready=False/Unknown** : problème de communication avec le nœud ou d'état node; relever la durée, les effets sur les Pods et la répartition.
- **MemoryPressure / DiskPressure** : conditions de pression qui peuvent affecter scheduling, éviction et I/O; distinguer les observations des causes sous-jacentes.
- **MCP Degraded** : examiner la cause rapportée; ne pas éditer les MachineConfigs en urgence sans procédure.
- **Operator Degraded** : collecter Conditions, raisons et Events; la dégradation d'un Operator peut être indépendante du trafic métier.
- **CPU 20 % dans \`top\`** : n'établit pas qu'un nouveau Pod est schedulable; comparer requests et allocatable.

Sur CRC mono-nœud, un unique problème de machine concentre plusieurs domaines de panne. La topologie rend la preuve de HA inter-nœuds impossible.

## 5. Séquence applicative : API → Deployment → Pod

~~~bash
oc -n NAMESPACE get deployments
oc -n NAMESPACE get replicasets
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE describe deployment NOM_DEPLOYMENT
oc -n NAMESPACE describe pod NOM_POD
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

### 5.1 Pod Pending

Examiner d'abord \`spec.nodeName\`, les raisons de scheduling et les ressources demandées. Causes possibles : requests dépassant allocatable, taints, affinité, volume/topologie, limite du nombre de Pods. **Quota/admission** peut refuser la création en amont d'un Pod Pending : garder cette distinction.

### 5.2 ContainerWaiting

- \`ImagePullBackOff\` : nom de l'image, autorisations de registre, proxy, DNS, CA, image architecture.
- \`CreateContainerConfigError\` : objets de configuration ou secrets attendus, erreurs de spec.
- \`CrashLoopBackOff\` : erreur de process, exit code, probes, OOM, dépendance; consulter log et état précédent si disponible, avec protection des secrets.
- \`ContainerCreating\` durable : volume/CSI, réseau CNI ou runtime peuvent être en cause.

### 5.3 Running mais non Ready

Ne pas tuer le Pod par défaut. Vérifier readiness, ports, endpoint, durée de démarrage, dépendances, budget CPU et erreurs applicatives. La liveness peut provoquer des redémarrages, tandis que readiness peut retirer le Pod du Service sans arrêter le conteneur.

## 6. Réseau : commencer par le dernier objet stable

~~~bash
oc -n NAMESPACE get svc NOM_SERVICE -o yaml
oc -n NAMESPACE get endpointslices -l kubernetes.io/service-name=NOM_SERVICE
oc -n NAMESPACE get routes
oc -n NAMESPACE get networkpolicies
oc get clusteroperator/dns
oc get clusteroperator/ingress
~~~

Trois situations :

1. **0 endpoint ready** : hypothèses labels, readiness, ports, EndpointSlice controller; pas d'abord DNS externe.
2. **Endpoints prêts, connexion refusée** : port, listener, NetworkPolicy, routage réseau, TLS.
3. **Connexion HTTP réussie, requête métier échoue** : authN/authZ, DB, broker, timeout, contrat API, données.

Un code 503 ou 504 peut être émis par plusieurs couches; il faut rechercher la **source** de la réponse et un identifiant de corrélation, pas simplement le chiffre.

## 7. Stockage et données : ne jamais improviser de nettoyage

~~~bash
oc -n NAMESPACE get pvc
oc -n NAMESPACE describe pvc NOM_PVC
oc get storageclass
oc get csidrivers
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

\`PVC Pending\` peut être normal avec \`WaitForFirstConsumer\` sans consommateur éligible. \`PVC Bound\` ne garantit pas attach et mount réussis. \`RWO\` signifie un nœud, pas exclusivement un Pod. Ne pas supprimer des PVC « anciens » avant de connaître propriétaire, finalizers, reclaimPolicy et présence de données à conserver.

### 7.1 Exemple de raisonnement : problème de stockage ou de ressources ?

Symptôme : une instance StatefulSet reste Pending. Vérifier :
- Events du Pod : \`FailedScheduling\`, \`volume node affinity conflict\` ?
- PVC : Pending ou Bound, StorageClass, mode de binding ?
- StorageClass : \`WaitForFirstConsumer\` ?
- Capacités et contraintes de topology sur les workers ?
- Conditions CSI / quotas / reclaim ?

**Décision** : ne pas conclure à « manque de mémoire » sans preuve CPU/mémoire, et ne pas créer un volume supplémentaire sans vérifier l'espace restant et le mode de binding.

## 8. Reconciliation GitOps et Operator : un troisième type de problème

Une application peut être Running et pourtant présenter du drift, ou une CR peut être Ready=False alors que les Pods existent. Si GitOps et un Operator gèrent les mêmes champs, ils peuvent se contredire. La preuve attendue comprend :

- commit Git et révision d'application déclarée;
- champs et propriétaire dans \`metadata.managedFields\`;
- génération de la CR, \`status.observedGeneration\` lorsque pertinent;
- Conditions, Events et erreurs du reconciler;
- état réellement observé des ressources dérivées.

**Ne pas** activer \`--force-conflicts\` ou \`prune\` pour « faire disparaître le drift » sans documenter la source de vérité et l'effet sur les données.

## 9. Prioriser les hypothèses et éviter les changements simultanés

Un triage efficace procède par expériences discriminantes :

| Hypothèse | Observation discriminante | Alternative à exclure |
|---|---|---|
| Readiness cassée | Endpoints absents + probe en erreur | Label/selector incompatible |
| Problème d'image | Events ImagePullBackOff | SCC/permissions runtime après téléchargement |
| Saturation CPU | Mesures de throttling et latence | Timeout externe, pool de connexions |
| DNS cluster dégradé | ClusterOperator DNS, erreurs de résolution | NetworkPolicy du seul namespace |
| Mauvais binding PVC | Events PVC + StorageClass + topology | Pod non schedulable pour une autre raison |
| Régression GitOps | Dégradation immédiatement après révision précise | Défaillance de dépendance indépendante |
| IdP indisponible | Erreurs de validation token / clés | Défaut d'autorisation métier pour un client |

Les métriques de corrélation ne suffisent pas toujours à établir la causalité. Chaque conclusion doit dire ce qui la confirmerait ou la réfuterait.

## 10. Restauration : valider l'effet métier

Une fois la cause traitée par l'équipe habilitée, valider au minimum :
1. nombre de requêtes réussies sur une fenêtre représentative;
2. taux d'erreurs et latences revenu au niveau SLO;
3. endpoints, Pods et dépendances stabilisés;
4. absence de pertes de messages, de doublons ou d'incohérences non résolues;
5. contrôles réseau, sécurité et stockage toujours en place;
6. procédure de rollback et de suivi post-incident documentée.

Il ne suffit pas de voir le Pod Running après un redémarrage. Un redémarrage peut masquer la cause, effacer des indices et créer des effets secondaires.

## 11. Artefact de preuve N3

~~~text
INCIDENT_ID : <anonymisé>
T0 / Fuseau : <horodatage>
Service / Contrat métier : <description sans PII>
Symptôme utilisateur : <mesure SLI>
Hypothèses initiales : <liste bornée>
Observations read-only : <commande, heure, résultat expurgé>
Hypothèses réfutées : <preuve>
Cause retenue : <preuve causale ou statut "non confirmée">
Action autorisée : <référence du changement, responsable>
Mesure après action : <SLI et fenêtre>
Impact sur données : <intégrité, messages, sauvegarde>
Risque résiduel / actions préventives : <suivi>
~~~

Le protocole doit protéger les tokens, dumps d'objets, identifiants de paiement et données réglementées.

## 12. Laboratoire offline : triage reproductible

Le [Lab L08](../../labs/08-offline-n3-triage.md) utilise un fichier JSON de **signaux fictifs** et un moteur Python qui retourne des **priorités d'investigation**, pas des causes prétendument confirmées. Les tests couvrent les cas d'absence d'endpoint, PVC Pending, DNS Degraded et des signaux contradictoires.

L'outil n'appelle pas \`oc\`, ne lit aucun kubeconfig et ne contacte aucun cluster. Une réussite des tests atteste de la logique pédagogique, pas de la fiabilité d'une vraie investigation.

## Sources

- [Kubernetes — Debugging Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Kubernetes — Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Kubernetes — Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Red Hat — DNS Operator 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/networking_operators/dns-operator)
- [Red Hat — Network security 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html-single/network_security/index)

**Statut final à obtenir** : revue technique, simulation négative passée, tests sur infrastructure autorisée et preuves expurgées. Aucun diagnostic runtime n'a été exécuté pour ce chapitre.
