# 01 — Pourquoi OpenShift ? Du conteneur à une plateforme d'entreprise

**Volume** : 01 · **Niveau** : Foundations → Architecte · **Statut** : DRAFT  
**Base documentaire** : OpenShift Container Platform 4.22 · **Preuve** : PUBLIC_VERIFIED  
**Dernière vérification des références** : 2026-10-11

## Objectifs d'apprentissage

À l'issue du chapitre, le lecteur doit pouvoir :
- Distinguer conteneur, orchestrateur Kubernetes et plateforme OpenShift.
- Décrire le rôle d'une API déclarative et d'une boucle de réconciliation.
- Expliquer pourquoi l'administration de la plateforme ne s'arrête pas à la gestion des Pods.
- Évaluer les responsabilités techniques et opérationnelles transférées ou ajoutées par OpenShift.
- Identifier les premiers arbitrages d'architecture pour une plateforme d'entreprise.

## 1. Le problème initial : produire et opérer des services à grande échelle

Un programme applicatif doit maintenir des services disponibles malgré les défaillances, les mises à jour et les variations de demande. Sans orchestrateur, les équipes gèrent directement des machines, des processus, des adresses, des déploiements, les redémarrages et la distribution de charge. Cette approche devient difficile à standardiser et à auditer à grande échelle.

Le **conteneur** empaquette une application et ses dépendances dans une forme exploitable par un runtime compatible. Il n'apporte pas, à lui seul, une garantie de disponibilité, un réseau de services ou une orchestration. **Kubernetes** expose des ressources et des contrôleurs qui rapprochent en permanence l'état observé de l'état désiré. **OpenShift Container Platform (OCP)** construit sur Kubernetes un ensemble cohérent de mécanismes pour installer, sécuriser, mettre à jour et exploiter une plateforme applicative.

Cette distinction est essentielle : dire « nous avons Docker ou une image OCI » ne signifie pas « nous avons une plateforme ». Dire « nous avons Kubernetes » ne décrit pas encore comment sont opérés les identités, la sécurité, les mises à jour du plan de contrôle, les registres, la conformité ou le support.

## 2. Trois niveaux à ne jamais confondre

| Niveau | Question | Exemples de responsabilités |
|---|---|---|
| Image et runtime | Comment exécuter isolément un processus ? | Format d'image, exécution, ressources, filesystem |
| Orchestration Kubernetes | Comment déclarer et maintenir des workloads distribués ? | API, Pods, scheduling, Services, controllers |
| Plateforme OpenShift | Comment industrialiser et opérer cet ensemble ? | Distribution, Operators, OS des nœuds, réseau, authentication, console, lifecycle |

Un administrateur pilote des ressources déclaratives; un SRE évalue leur comportement; un architecte conçoit les frontières, les NFR et la trajectoire de plateforme. Ces rôles sont complémentaires, non interchangeables.

## 3. Vue logique des couches

~~~mermaid
flowchart TB
  U[Équipes applicatives et exploitation]
  A[API OpenShift et API Kubernetes]
  P[Capabilities plateforme: auth, routes, monitoring, operators]
  C[Control plane: API server, etcd, scheduler, controllers]
  W[Workers: kubelet, CRI-O, réseau et volumes]
  I[Infrastructure: bare metal, virtualisation ou cloud]
  U --> A
  A --> P
  A --> C
  C --> W
  P --> W
  W --> I
~~~

C'est un **modèle pédagogique**, pas une représentation de toutes les dépendances internes. Par exemple, les Operators sont des contrôleurs s'appuyant sur les API Kubernetes/OpenShift et peuvent gérer des composants du plan de contrôle ou des capacités applicatives.

## 4. Ce qu'OpenShift apporte en particulier

OpenShift intègre notamment des composants opérés par des Operators, une console d'administration, l'outil **oc**, des fonctions de routage et d'authentification, et une stratégie de cycle de vie de plateforme. Dans OCP 4.22, les nœuds du plan de contrôle utilisent RHCOS, avec notamment CRI-O et kubelet. Les Operators de plateforme participent à la gestion de son état et de ses mises à jour.

Ces capacités n'éliminent pas les responsabilités de l'équipe plateforme : conception réseau, architecture d'identité, capacité, coûts, sécurité applicative, sauvegardes, observabilité et politique de changements restent des domaines à gouverner. Un produit ne transforme pas automatiquement toute charge de travail en application résiliente.

## 5. De la demande métier au choix d'architecture

Prenons un service de paiements avec un objectif de disponibilité élevé, des périodes de pointe et des données réglementées. Avant de choisir un cluster, un architecte doit cadrer :

1. **SLO et criticité** : quel service doit être accessible, avec quel niveau de dégradation tolérable ?
2. **Failure domains** : quels événements doivent être supportés — Pod, nœud, zone ou site ?
3. **RPO/RTO** : quelles pertes de données et durées d'interruption sont tolérées ?
4. **IAM et ségrégation** : quels utilisateurs, services et équipes accèdent à quoi ?
5. **Observabilité** : quels symptômes et signaux permettent de vérifier les SLO ?
6. **Delivery** : quel chemin auditable du commit à la production ?
7. **Coût/énergie** : quels critères de dimensionnement et de sobriété ?
8. **Supportabilité** : quelles versions, dépendances et fenêtres d'évolution ?

Le choix OpenShift doit être justifié par des contraintes et des bénéfices mesurables — pas uniquement par l'existence de workloads conteneurisés.

## 6. OpenShift n'est pas une garantie de « production-ready »

Quelques anti-patterns :
- Assimiler un cluster CRC à un cluster de production hautement disponible.
- Déduire la résilience applicative de plusieurs replicas alors que la base reste un SPOF.
- Exposer une Route et conclure que la sécurité réseau est complète.
- Assimiler une ressource Synced dans GitOps à la qualité métier du service.
- Déployer un Operator et supposer que tous les cycles de sauvegarde et de reprise sont couverts.

Pour chaque promesse, relier l'affirmation à un test : scénario de panne, métrique, résultat et limite.

## 7. Observation : premières commandes sûres

Les commandes suivantes **ne modifient pas** les ressources. Elles exigent un client oc connecté et des droits de lecture appropriés :

~~~bash
oc whoami
oc version
oc get clusterversion
oc get nodes
oc get clusteroperators
oc get projects
~~~

La sortie de **oc whoami** peut identifier un utilisateur : ne pas la publier sans anonymisation. Ne pas diffuser de kubeconfig ni de jeton. Les ressources non accessibles peuvent provoquer des erreurs RBAC; cela n'est pas forcément un dysfonctionnement de cluster.

Voir l'[atelier complet](../../labs/01-cluster-read-only.md).

## 8. Revue d'architecture : questions de départ

**Question : OpenShift remplace-t-il Kubernetes ?** Non. OpenShift est construit sur Kubernetes et ajoute une distribution et des capacités d'exploitation intégrées.

**Question : le nombre de replicas d'un Deployment suffit-il à valider le HA ?** Non. Il faut analyser placement, quorum, stockage, dépendances et domaines de panne.

**Question : comment reconnaître une preuve de fonctionnement ?** Elle indique le cluster, les versions, le protocole, la date, le résultat, les limites et les éléments permettant une vérification.


## 9. La chaîne complète : de l'exigence métier à un service observable

Prenons une application qui reçoit une requête HTTP, interroge un moteur de décision puis publie un événement métier. La chaîne traverse plusieurs responsabilités :

~~~mermaid
flowchart LR
  U[Utilisateur] --> E[DNS / accès réseau]
  E --> I[Ingress / Route]
  I --> S[Service]
  S --> A[Pod applicatif]
  A --> D[Moteur de décision externe]
  A --> MQ[File de messages]
  A --> OBS[Traces, logs, métriques]
  CD[Chaîne CI/CD et registre] --> G[GitOps]
  G --> API[API Kubernetes/OpenShift]
  API --> C[Contrôleurs]
  C --> A
~~~

Un architecte doit expliciter les **contrats** entre ces composants. L'orchestrateur peut recréer un Pod disparu; il ne peut pas garantir que le moteur de décision produit un résultat métier correct, que le destinataire MQ est disponible ni que l'utilisateur dispose d'un jeton valide.

### 9.1 Contrats techniques par frontière

| Frontière | Contrat vérifiable | Mode de panne | Premier signal |
|---|---|---|---|
| Client → entrée | DNS, TLS, authentification | Erreur de résolution, certificat invalide | Taux d'erreurs client et logs ingress |
| Entrée → Service | Route/Ingress, Service, endpoints éligibles | Aucune cible Ready | EndpointSlice, erreurs 503 |
| Service → Pod | Port, readiness, réseau autorisé | Refus réseau ou process non prêt | Probe, NetworkPolicy, logs |
| Application → décision | Timeout, identité, version de contrat | Délais excessifs, réponse incohérente | Latence par dépendance et erreurs |
| Application → broker | Stratégie de publication et d'acquittement | Messages en attente, doublons | Queue depth, age, retries |
| Git → runtime | Révision, digest, droits d'accès | Drift, image non autorisée | État GitOps, admission, rollout |
| Observabilité | Corrélation bout-en-bout | Diagnostic impossible | Taux de traces exploitables |

Un « vert » de monitoring pour la couche Kubernetes n'implique donc pas automatiquement un « vert » métier. À l'inverse, une dégradation métier ne prouve pas que la cause est OpenShift.

### 9.2 Les cinq plans d'une architecture d'entreprise

Au lieu de réduire le dossier à un diagramme de Pods, distinguer :

1. **Plan métier** : parcours utilisateur, transactions, risques, confidentialité, criticité.
2. **Plan applicatif** : frontières de services, contrats d'API, schémas d'événements, dépendances.
3. **Plan plateforme** : clusters, namespaces, controllers, workers, réseau, stockage, identité.
4. **Plan exploitation** : SLO, alertes, runbooks, astreintes, sauvegardes, changements.
5. **Plan gouvernance** : responsabilités, policies, ADR, coût, Green IT, audit et versionnement.

Un schéma de niveau 3 ne saurait répondre seul à une question de niveau 1 ou 4. Le dossier d'architecture doit relier ces plans par exigences, décisions et preuves.

## 10. La séparation des responsabilités selon le modèle d'exploitation

« OpenShift » désigne une technologie, pas une responsabilité unique. Une équipe qui administre un cluster autogéré doit traiter notamment le dimensionnement, les machines, les cycles de vie et les dépendances d'infrastructure. Un service managé déplace **certaines** opérations vers son fournisseur, sans supprimer les obligations sur l'application, les données ou les politiques d'accès.

| Domaine | Cluster autogéré (exemple) | Offre managée (exemple) | Question à contractualiser |
|---|---|---|---|
| Plan de contrôle | Équipe cluster, selon support éditeur | Fournisseur selon service | Qui rétablit l'API et dans quel délai ? |
| Machines et OS | Équipe infrastructure / plateforme | Répartition variable selon offre | Qui applique les patches et valide la fenêtre ? |
| IAM/RBAC applicatifs | Équipe plateforme + sécurité | Toujours gouvernance du client | Qui accorde et révoque les privilèges ? |
| Données et backup | Propriétaire de la donnée + infra | Responsabilités variables | Qui garantit restauration et cohérence ? |
| SLO métier | Propriétaire du service | Propriétaire du service | Comment mesure-t-on la vraie transaction ? |
| Déploiement d'applications | Équipe delivery | Équipe delivery | Qui approuve et peut revenir en arrière ? |

Cette matrice est une **méthode**. Pour un contrat réel, comparer les conditions de service spécifiques et non appliquer universellement une séparation « fournisseur/client ».

## 11. Comparer trois scénarios plutôt que choisir par habitude

### Scénario A — Petite API stateless de démonstration

Hypothèses : un environnement de formation, quelques connexions, peu de données, objectifs pédagogiques. Le critère principal est le temps d'apprentissage. CRC peut suffire à observer les API, les Pods, les Routes ou certains Operators si les ressources et droits existent. Il ne valide pas le HA multinœud.

### Scénario B — API critique avec dépendance persistante

Hypothèses : exigences de service, authentification d'entreprise, historisation des transactions, incidents audités. Le cluster doit être dimensionné, segmenté et exploité selon des SLO; l'architecture des bases et brokers exige une analyse indépendante. Un StatefulSet ne constitue pas un plan de PRA. Des tests de panne et de restauration sont nécessaires.

### Scénario C — Plusieurs équipes et plusieurs environnements

Hypothèses : équipes produit autonomes, séparation dev/préproduction/production, dizaines de services. La décision porte sur les APIs de plateforme, l'IDP, les golden paths, la gouvernance GitOps, les quotas, le support et le coût agrégé. La notion de **produit plateforme** prend plus de valeur que celle d'un simple cluster.

### 11.1 Matrice de décision

Noter chaque dimension de 1 à 5 **sur des mesures locales** plutôt que sur une réputation produit :

| Dimension | Mesure à collecter | Pourquoi cela compte |
|---|---|---|
| Temps de mise à disposition | Durée demande → namespace exploitable | Expérience développeur |
| Standardisation | % services appliquant les contrats plateforme | Dette d'exploitation |
| Résilience | Pannes survivables réellement testées | Continuité de service |
| Sécurité | Contrôles d'admission et audits réussis | Maîtrise du risque |
| Réversibilité | Restauration et rollback mesurés | Limitation du blast radius |
| Efficacité ressources | CPU/RAM demandés et consommés par service | Capacité et coûts |
| Évolutivité | Effort et risque d'upgrade sur version cible | Soutenabilité |

La bonne comparaison inclut Kubernetes intégré soi-même, OpenShift autogéré, une offre Kubernetes managée, éventuellement des VMs conventionnelles. Aucune technologie ne remporte d'avance tous les critères.

## 12. Analyse de capacité : distinguer besoin, allocation et performance

Considérons un cas **entièrement hypothétique**, sans référence à une machine ni une promesse de performance :

- 8 services, chacun avec 3 replicas, soit 24 Pods applicatifs;
- request = 300 millicores et 384 Mi par Pod;
- overhead infra et système **non inclus** ;
- une pointe nécessite un facteur multiplicateur de 1,8 sur les replicas disponibles.

Demandes applicatives initiales :

- CPU : 24 × 0,3 = **7,2 CPU**;
- mémoire : 24 × 384 Mi = **9 216 Mi = 9 Gi**.

Avec 1,8 fois autant de replicas, il faut arrondir chaque groupe à un entier : 3 × 1,8 = 5,4, donc **6 replicas par service** et 48 Pods. Ce scénario impose alors 48 × 0,3 = **14,4 CPU** de requests et 48 × 384 Mi = **18 Gi** de requests mémoire.

Ce calcul ne suffit **pas** pour un dimensionnement : il faut ajouter les DaemonSets, composants plateforme, marge de défaillance, répartition des nœuds, limits, stockage et capacité de chaque dépendance. Pour des contraintes fortes, il faut mesurer CPU-seconde/transaction, mémoire de pointe, p95/p99, impact des probes et des GC, saturation IO et réseau, puis simuler un domaine de panne.

### 12.1 Le piège d'un cluster affichant « 20 % CPU »

Un cluster peut être sous-utilisé instantanément et pourtant refuser de nouveaux Pods parce que les **requests** occupent la capacité allocatable. Le nombre de Pods maximal, les taints, le stockage, la topologie et les quotas peuvent également interdire un placement. Il faut comparer **demandes réservées et capacité allocatable**, et non se limiter aux métriques de consommation.

### 12.2 FinOps et Green IT dès la conception

La bonne métrique n'est pas uniquement le coût d'un nœud ou son TDP. Pour une application donnée, documenter :

- volume de transactions significatives par période;
- ressources réellement consommées **et** ressources réservées;
- taux d'occupation de la plateforme et pertes dues au surprovisionnement;
- énergie observée, si une mesure existe, ou estimation explicitement annotée;
- émissions estimées avec facteur d'émission, lieu et période documentés;
- capacité de faire évoluer les replicas sans détériorer les SLO.

Une baisse des requests peut augmenter le bin-packing mais aussi dégrader la résilience sous contention; la sobriété n'est pas simplement « diminuer toutes les limites ».

## 13. Première revue d'architecture : dossier minimal utilisable

À produire avant un engagement de plateforme :

~~~text
ADR-001 : choisir le modèle d'hébergement
Contexte : contraintes de disponibilité, données, localisation, réseau.
Options : OCP autogéré / OCP managé / autre orchestrateur / VMs.
Décision : à instruire avec critères pondérés.
Conséquences : responsabilité, coût récurrent, dette d'exploitation.

ADR-002 : frontières des environnements
Contexte : séparation des équipes, secrets, blast radius et conformité.
Options : namespaces / clusters / comptes ou souscriptions distincts.
Décision : guidée par risque et gouvernance, pas par nombre de projets.

ADR-003 : exposition et segmentation réseau
Contexte : clients internes/externes, identité, TLS, appels tiers.
Preuve attendue : tests flux positifs/négatifs + diagramme de confiance.

ADR-004 : continuité et données
Contexte : dépendances stateful, RPO/RTO, sauvegardes.
Preuve attendue : procédure restore, mesure du temps, contrôle d'intégrité.

ADR-005 : livraison et retour arrière
Contexte : exigences d'audit, supply chain et responsabilité.
Preuve attendue : commit → image digest → approbation → déploiement.
~~~

Un dossier « complet » contient les décisions **et** leurs limites. Dans un environnement de démonstration, les validations non réalisées doivent rester signalées comme telles.

## 14. Atelier papier : diagnostic de dégradation métier

**Situation pédagogique** : après un déploiement, trois replicas sont Running. L'ingress répond 200 aux sondes, mais le taux d'échec fonctionnel a doublé.

1. Distinguer les hypothèses sur le front HTTP, l'authentification, la base, le moteur de décision et la publication MQ.
2. Nommer un signal discriminant par hypothèse.
3. Construire une chronologie « commit → digest → déploiement → changement de métrique ».
4. Identifier les conditions d'un rollback applicatif sûr (contrat de base et d'événements compris).
5. Déterminer quelles observations pourraient être produites sur CRC sans altérer les workloads.

**Corrigé synthétique** : constater la réussite d'une probe n'autorise pas à conclure au succès métier. La première décision doit dépendre de métriques de parcours, de traces corrélées, d'erreurs par dépendance et de la comparaison des versions. Un rollback applicatif peut être inadapté si une migration de données non réversible a déjà eu lieu. Ce scénario reste une **REFERENCE_ARCHITECTURE**, sans exécution sur un cluster.

## Références

- [Red Hat — OpenShift Container Platform 4.22, architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — OpenShift Container Platform 4.22, overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/overview/ocp-overview)
- [Red Hat — OpenShift Container Platform 4.22, Operators overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview)

**Limite** : cette édition décrit des concepts et références documentaires, pas un nouveau test exécuté sur le CRC de l'auteur.
