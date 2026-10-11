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

## Références

- [Red Hat — OpenShift Container Platform 4.22, architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — OpenShift Container Platform 4.22, overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/overview/ocp-overview)
- [Red Hat — OpenShift Container Platform 4.22, Operators overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview)

**Limite** : cette édition décrit des concepts et références documentaires, pas un nouveau test exécuté sur le CRC de l'auteur.
