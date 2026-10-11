# 05 — Kubernetes : API, contrôleurs, scheduling et primitives d'architecture

**Volume 01 · EDITION_1_CONTENT_COMPLETE · Niveau : administrateur → architecte**  
**Portée : concepts Kubernetes documentés ; application OpenShift 4.22**  
**Preuve : PUBLIC_VERIFIED ; tous les YAML ci-dessous sont des exemples explicatifs non déployés.**

## Objectifs et prérequis

À l'issue de ce chapitre : reconstruire le cycle complet d'une requête API; expliquer les rôles de Deployment, ReplicaSet, Pod, Service et EndpointSlice; raisonner sur scheduler, quota et disponibilité; différencier requests, limits, probes, disruption et autoscaling; diagnostiquer un état Pending ou une Route qui n'achemine aucun trafic.

Les prérequis sont les chapitres Linux et OCI du Volume 01.

## 1. Déclaratif ne signifie pas exécution instantanée

Kubernetes implémente des API et des boucles de contrôle. L'application d'une ressource est **une intention enregistrée**, pas une promesse de succès immédiat. Chaque contrôleur cherche à produire l'état désiré puis rapporte l'état observé, avec des délais et des possibilités d'échec.

L'objet possède typiquement :

- **apiVersion / kind** : famille d'API et type.
- **metadata** : nom, namespace si applicable, labels, annotations, génération, ownerReferences, finalizers.
- **spec** : état désiré, si l'objet est de cette catégorie.
- **status** : observations rapportées par des composants du système.

Les labels servent à sélectionner des ressources; les annotations stockent des métadonnées non utilisées comme sélecteurs. Les ownerReferences rendent explicite une relation propriétaire/dépendant et guident le garbage collector; elles ne remplacent pas la connaissance fonctionnelle des dépendances. Les finalizers empêchent de finaliser immédiatement la suppression tant que le contrôleur responsable n'a pas effectué son nettoyage.

L'API Kubernetes comprend un groupe historique `v1` (par exemple Pod, Service et Secret) et des groupes nommés tels que `apps/v1` pour Deployment et StatefulSet. Une version d'API n'est pas la même chose que la version du cluster.

## 2. Le cycle de vie d'un Deployment

~~~mermaid
sequenceDiagram
  participant Eng as Ingénieur
  participant API as kube-apiserver
  participant ETC as etcd
  participant DC as Deployment controller
  participant RS as ReplicaSet controller
  participant S as scheduler
  participant K as kubelet
  participant CRI as CRI-O
  Eng->>API: demande de création / modification Deployment
  API->>API: AuthN, AuthZ, admission, validation
  API->>ETC: persistance de l'intention
  DC->>API: observe le Deployment
  DC->>API: crée/ajuste ReplicaSet
  RS->>API: crée/ajuste Pods
  S->>API: lie un Pod Pending à un nœud éligible
  K->>API: observe le Pod assigné
  K->>CRI: prépare les conteneurs
  CRI-->>K: état de démarrage
  K->>API: status Pod / conditions
  API-->>Eng: lecture des états observés
~~~

Il s'agit d'une **séquence conceptuelle simplifiée** : les contrôleurs réagissent à des événements et vérifient continuellement l'état; ce n'est pas un pipeline impératif entièrement synchrone. La création de l'objet ne garantit ni téléchargement d'image, ni disponibilité de volume, ni readiness.

### Différentes définitions de « prêt »

- **Pod Running** : le Pod est lié à un nœud et au moins un conteneur s'exécute (ou redémarre); ce n'est pas la disponibilité applicative.
- **Pod Ready** : sa condition de readiness répond aux critères configurés; dépend des probes et autres conditions.
- **Deployment Available** : répliques disponibles selon les conditions du Deployment, notamment minReadySeconds.
- **Service routable** : existence de backends éligibles dans les EndpointSlices et réseau effectif.
- **SLO métier atteint** : l'application rend effectivement les services avec latence et erreurs acceptables.

Un objet Synced en GitOps ou un Deployment Available ne fournit **pas** de preuve suffisante que la transaction métier aboutit.

## 3. Workloads : choisir le bon contrôleur

| Type | Mission | Choix fréquent | Limite / risque |
|---|---|---|---|
| Pod nu | Unité d'exécution minimale | Diagnostic ou cas contrôlé | Aucun contrôleur de remplacement de haut niveau |
| Deployment | Workload stateless à mise à jour progressive | API HTTP, workers interchangeables | Pas d'identité stable ni de disque individuel garanti |
| StatefulSet | Identité ordonnée/stable des instances, PVC persistants | Base distribuée, broker selon design | N'assure pas à lui seul consensus, backups ou HA |
| DaemonSet | Un Pod par nœud éligible | Agents de log, réseau, sécurité | Impact proportionnel aux nœuds, risque de ressources |
| Job | Travail borné à completion | Batch, migration sous contrôle | Idempotence, relances et collisions à concevoir |
| CronJob | Planification périodique de Jobs | Traitements planifiés | Retards/doublons possibles, calendrier non équivalent à exactly-once |

**Critère d'architecture** : ce n'est pas le packaging Docker qui décide du contrôleur, mais les propriétés de l'application — état, identité, ordre, disponibilité, réessais, temporalité.

## 4. Exemple complet d'objets — revue de conception hors cluster

Cet exemple est **ILLUSTRATIVE_ONLY**. Il utilise une image et un digest fictifs : **ne pas appliquer sans remplacer l'image, tester ses permissions et adapter les politiques**.

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-reader
  namespace: poc-reference
  labels:
    app.kubernetes.io/name: payment-reader
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: payment-reader
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payment-reader
    spec:
      terminationGracePeriodSeconds: 30
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: api
          image: registry.example.invalid/payment-reader@sha256:REPLACE_WITH_VALID_DIGEST
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 384Mi
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: http
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: payment-reader
  namespace: poc-reference
spec:
  selector:
    app.kubernetes.io/name: payment-reader
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
  type: ClusterIP
~~~

### Analyse de ce manifeste

1. **Références** : `spec.selector.matchLabels`, les labels du PodTemplate et le sélecteur du Service doivent correspondre. Sinon un Service peut rester sans backend.
2. **Noms** : `targetPort: http` doit référencer le nom du port du conteneur.
3. **Requests** : les 2 replicas demandent ensemble au minimum 200m CPU et 256Mi mémoire; ces valeurs n'incluent pas les sidecars éventuels et l'overhead.
4. **Limits** : chaque container a un plafond CPU de 500m et mémoire 384Mi. Ce sont des propriétés de chaque conteneur, pas un plafond global « pour le Deployment ».
5. **Readiness** : /ready doit être réellement implémenté; un code HTTP de santé superficiel peut masquer une panne des dépendances métier.
6. **Liveness** : /health ne doit pas provoquer des redémarrages systématiques pendant une dépendance temporairement indisponible.
7. **SCC** : l'UID, les groupes et les droits du processus seront déterminés par la politique d'admission et l'image; ne pas supposer que runAsNonRoot suffit à garantir le démarrage.
8. **Disponibilité** : deux replicas sur le même nœud ne procurent aucune survie à sa panne. Un spread topology adapté ne peut être démontré sur un CRC à un seul nœud.
9. **Route** : non incluse; le Service ClusterIP est interne.
10. **Secret** : aucun n'est requis pour cet exemple de lecture; ne jamais mettre un secret en clair dans un manifest publiable.

Le YAML est illustratif parce que l'image n'existe pas et que les endpoints ne sont pas implémentés. **Aucun déploiement effectif n'est revendiqué**.

## 5. Scheduling : filtrer puis départager

Le scheduler Kubernetes sélectionne un nœud pour un Pod non affecté. L'analyse peut être vue en deux phases pédagogiques : trouver les nœuds **éligibles** (filtrage), puis départager les candidats par des scores selon les plugins et la configuration. Les détails précis dépendent de la version et du profil.

Principaux facteurs :

- Ressources demandées vs ressources allocatables déjà réservées par les Pods.
- Node selectors et affinités de nœuds (hard/soft).
- Taints et tolerations.
- Contraintes topologySpread et inter-Pod affinity/anti-affinity.
- Volumes/PV et contraintes topologiques de stockage.
- Topologie disponible et configuration scheduler.

### Exemple de placement

Un cluster possède :
- Nœud A : 4 CPU allocatables, 1 CPU déjà demandé par les Pods.
- Nœud B : 4 CPU allocatables, 3,5 CPU déjà demandés.
- Nouveau Pod : 1 CPU demandé.

Pour le seul critère CPU, A est admissible (3 CPU non demandés avant son arrivée), tandis que B ne l'est pas (0,5 CPU non demandé). Mais même A pourrait être rejeté à cause d'un taint ou du stockage. Une limite CPU de 4 CPU n'est pas le critère principal de filtrage ici : ce sont les **requests**, combinées aux politiques, qui comptent.

### Nœud « plein » malgré du CPU libre

Le scheduler se base sur les ressources **demandées**, pas uniquement sur les métriques `oc adm top nodes`. Un nœud affichant 20 % de CPU consommé peut ne pas accepter de nouveaux Pods si la somme des requests a épuisé son allocatable, s'il est atteint par la limite du nombre de Pods ou si d'autres contraintes s'opposent au placement.

## 6. Qualité de service et perturbations

### QoS et mémoire

Les classes Kubernetes **Guaranteed**, **Burstable** et **BestEffort** dépendent de la définition des requests/limits CPU/mémoire. Elles influencent notamment les comportements sous pression, mais ne constituent pas une assurance de survie à toutes les évictions.

### Probes

- **startupProbe** : laisse démarrer les applications lentes avant application des autres probes.
- **readinessProbe** : retire temporairement un Pod des backends prêts quand sa vérification échoue.
- **livenessProbe** : peut provoquer un redémarrage de conteneur. Ne pas la brancher sur une dépendance métier éphémère sans réfléchir.

Ces signaux doivent tester les bonnes propriétés. Exemple : une API dépend d'un moteur de décision externe; une simple réponse 200 à /health prouve que le serveur HTTP répond, pas que le moteur de décision est opérationnel.

### PodDisruptionBudget (PDB)

Un PDB limite certaines **évictions volontaires** via l'API d'eviction. Il ne protège pas d'une panne matérielle et n'oblige pas des réplicas à être sur des nœuds distincts. Sur un mono-nœud, il peut également bloquer ou gêner une maintenance voulue si mal configuré.

### Rollout

La stratégie RollingUpdate (maxUnavailable/maxSurge) pilote le rythme de remplacement pour un Deployment; la disponibilité pendant la transition dépend des ressources disponibles, probes et dépendances partagées. Un rollback Kubernetes ne restaure pas une base de données ni le contenu d'un PVC.

## 7. Service, EndpointSlice, DNS et réseau

Un Service de type ClusterIP expose une identité stable (nom DNS/IP virtuelle) vers des endpoints. Les EndpointSlices décrivent les backends et leurs caractéristiques, en fonction des Pods éligibles et du contrôleur. Les iptables/IPVS/eBPF/OVN utilisés pour acheminer le trafic dépendent de l'implémentation réseau du cluster.

~~~mermaid
flowchart LR
  CLIENT[Client dans un Pod] --> DNS[DNS de cluster]
  DNS --> SVC[Service ClusterIP]
  SVC --> EPS[EndpointSlices]
  EPS --> P1[Pod A ready]
  EPS --> P2[Pod B ready]
  P1 --> APP1[Container A]
  P2 --> APP2[Container B]
~~~

Ce schéma est **logique**, pas le chemin paquet exact; une requête DNS ne traverse pas un EndpointSlice, et le trafic est acheminé par le dataplane, non par l'objet API lui-même.

Dépannage en lecture seule :

~~~bash
oc -n NAMESPACE get svc NOM_SERVICE -o yaml
oc -n NAMESPACE get endpointslices -l kubernetes.io/service-name=NOM_SERVICE
oc -n NAMESPACE get pods -l app.kubernetes.io/name=NOM_APPLICATION -o wide
oc -n NAMESPACE get networkpolicies
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

L'absence de backends Ready fait suspecter les labels, les probes, l'état du Pod ou la configuration des ports. Si les EndpointSlices sont corrects mais les connexions échouent, poursuivre côté policy, résolution DNS, routage, listener applicatif et sécurité réseau.

## 8. Autoscaling et responsabilité de capacité

HPA adapte le nombre de replicas selon métriques/configuration, s'il est installé et configuré pour le workload. Ce mécanisme ne crée pas à lui seul des ressources dans le cluster. Le Cluster Autoscaler, lorsqu'il est disponible et correctement configuré, peut agir sur la capacité des machines; son domaine est différent.

Un architecte doit dimensionner au minimum :
- charge normale et pic (RPS, temps CPU par requête, taille des messages);
- requests/limits mesurés à charge réaliste;
- taille du cluster et marges d'exploitation;
- budgets de disruption et défaillance d'un domaine de panne;
- limites quotas, réseau, stockage et dépendances externes.

**Cas chiffré** : si un Pod consomme 200m CPU à 50 RPS dans un test représentatif, alors une extrapolation naïve à 500 RPS serait 2 CPU au total, hors variabilité, saturation, contention, I/O et croissance non linéaire. Cette estimation **INFERRED** est une première borne, pas un sizing de production.

## 9. Diagnostic N3 : Pod Pending

Ordre de vérification conseillé, **sans mutation** :

~~~bash
oc -n NAMESPACE get pod NOM_POD -o wide
oc -n NAMESPACE describe pod NOM_POD
oc -n NAMESPACE get events --field-selector involvedObject.name=NOM_POD
oc get nodes
oc describe node NOM_NODE
oc -n NAMESPACE get resourcequota,limitrange
oc -n NAMESPACE get pvc
~~~

La commande `describe node` peut exposer des informations d'infrastructure; vérifier la confidentialité avant partage. Si un Pod n'est pas assigné, le champ NOM_NODE peut être vide : consulter les Events et les nœuds candidats sans supposer qu'un nœud a déjà été choisi.

**Arbre de décision** :

1. Events « Insufficient cpu/memory » ? Examiner requests, allocatable et autres demandes.
2. « untolerated taint » ? Examiner politiques de nœuds et tolerations prévues.
3. « volume node affinity conflict » ? Examiner binding/zone du PV.
4. Node affinity/topology insatisfaites ? Examiner labels et placement voulu.
5. Quota ou LimitRange ? Une création peut être refusée avant même un Pod Pending; distinguer admission et scheduling.
6. Pod assigné mais conteneur ne démarre pas ? Passer du scheduling au diagnostic image/runtime/probes.

## 10. Questions de revue d'architecture

1. Pourquoi un Deployment à trois replicas n'est-il pas automatiquement hautement disponible ?
2. Pourquoi le CPU libre vu par `top` ne suffit-il pas à prévoir le scheduling ?
3. Que prouve exactement une readinessProbe ? Et que ne prouve-t-elle pas ?
4. Quel contrôleur utiliser pour une base nécessitant une identité stable ? Pourquoi le choix du StatefulSet ne valide-t-il pas la durabilité ?
5. Un Service sans EndpointSlice utile doit-il être « réparé » par une nouvelle Route ? Non : remonter les sélecteurs, readiness et ports avant l'exposition externe.
6. Un PDB assure-t-il la tolérance à la panne du nœud ? Non.
7. Quelle est la première preuve d'une admission SCC rejetée ? Les Events et erreurs d'admission; pas un changement de privilège au hasard.

## Références de travail

- [Kubernetes — Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Kubernetes — API overview](https://kubernetes.io/docs/reference/using-api/)
- [Kubernetes — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes — Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes — Assign Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Kubernetes — Scheduling and eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/)

**Vérification restante** : exécuter les commandes read-only sur un cluster autorisé, vérifier les statuts d'API effectifs et documenter chaque observation. Le YAML de démonstration n'est volontairement pas applicable sans adaptation.
