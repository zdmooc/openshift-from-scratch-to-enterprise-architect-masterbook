# 01 — Choisir une topologie et une méthode d'installation OpenShift

**Volume 03 · DRAFT · OpenShift Container Platform 4.22 · Source : guide d'installation officiel.**  
**Nature : décision d'architecture, non procédure exécutée.**

## Objectifs

À la fin de ce chapitre, savoir distinguer un laboratoire local CRC, un Single Node OpenShift, un cluster compact et un cluster de production standard; sélectionner une méthode IPI/UPI/Assisted/Agent-based selon le provider; identifier les dépendances de support et les points de panne qu'une topologie ne peut pas éviter.

## 1. Deux décisions différentes : topologie et méthode

Une **topologie** répond à « combien de nœuds, quels rôles, quelles zones de panne et quelles propriétés de disponibilité ? ».

Une **méthode d'installation** répond à « qui fournit les ressources d'infrastructure, comment l'installateur découvre les hôtes et quels prérequis doivent être disponibles au moment du bootstrap ? ».

Ces décisions sont interdépendantes, mais ne doivent pas être fusionnées. Un cluster à trois nœuds peut être installé par plusieurs méthodes selon le support du provider. Deux clusters utilisant IPI peuvent offrir des garanties de résilience très différentes si l'un est mono-zone et l'autre correctement réparti.

## 2. Comparer les topologies sans confondre laboratoire et production

| Topologie | Usage et avantages | Limites structurantes |
|---|---|---|
| CRC / OpenShift Local | POC d'API, GitOps, Operators et tests pédagogiques sur poste | Domaine de panne unique, CPU/RAM/disque contraints ; ne prouve pas HA multinœud |
| Single Node OpenShift (SNO) | Site edge, contrainte de ressources, opérations localisées | Pas de HA interne de nœud; panne hôte arrête les services locaux |
| Compact / three-node | Rôles de contrôle et compute co-localisés, pas de workers dédiés | Moins de marge pour les workloads et opérations de maintenance; dimensionnement strict |
| Control plane distinct + workers | Séparation de capacité workload et fonctions de contrôle | Coût et infrastructure supplémentaires, dépendances DNS/LB/PKI/etcd/stockage |
| Hosted control plane | Contrôle hébergé sur un management cluster, workers sur cluster hébergé | Dépendance forte au management cluster et au réseau inter-domaines |

**Prudence :** la documentation OCP 4.22 introduit également des topologies particulières à deux nœuds avec arbiter ou fencing, sous conditions de support et de provider. Elles ne remplacent pas universellement une configuration trois masters et ne doivent pas être copiées à partir d'un dessin.

### 2.1 Pourquoi SNO n'est pas un « petit cluster HA »

SNO réunit les fonctions essentielles sur une machine. Le [guide de préparation SNO 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_a_single_node/preparing-to-install-sno) rappelle qu'une installation Single Node ne se convertit pas simplement en configuration HA ou à deux nœuds après installation; le choix de topologie conditionne son cycle de vie.

SNO convient lorsque la disponibilité d'un seul hôte répond au besoin. Il est inadapté si le contrat exige la poursuite des services après perte du nœud. Un plan de remplacement et de restauration peut limiter les conséquences, mais il ne produit pas une continuité automatique.

### 2.2 Pourquoi CRC n'est pas SNO

CRC héberge un OpenShift Local virtualisé sur un poste; SNO est une méthode d'installation de cluster sur une machine cible, documentée par Red Hat pour certains scénarios edge ou low footprint. Les outils d'installation, contraintes de ressources, cycles de vie, licences et chemins d'évolution diffèrent.

Un \`oc get nodes\` affichant un seul nœud ne suffit donc pas à considérer CRC et SNO comme des produits ou déploiements interchangeables.

## 3. Méthodes IPI, UPI, Assisted et Agent-based

| Méthode | Autorité principale pour infrastructure | Cas de choix typique | Point de contrôle |
|---|---|---|---|
| IPI — Installer-provisioned infrastructure | Installateur et provider provisionnent une grande partie des ressources | Automatisation de création selon provider supporté | Credentials, quotas, réseau, sous-réseaux et droits |
| UPI — User-provisioned infrastructure | Client fournit et maintient les ressources requises | Infrastructure corporative spécifique, contraintes réseau/PKI | DNS/LB/hosts/bootstrap/IP et séquence d'installation |
| Assisted Installer | Service guidé découvrant les hôtes via média bootable | On-premises et cas supportés, réduisant le préflight manuel | Connectivité, inventaire matériel, architecture, credentials |
| Agent-based Installer | Média bootable et configuration déclarative locale | On-premises, notamment scénarios disconnected | Assets, manifests install-config, réseau et image RHCOS |

Le [guide officiel OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installation_overview/ocp-installation-overview) publie une matrice de compatibilité **provider × méthode**. Elle prévaut sur toute affirmation générale du type « IPI fonctionne partout ».

### 3.1 Une machine AWS n'est pas un hôte bare metal

Exemples de questions spécifiques au provider :

- AWS : rôles IAM, VPC, endpoints et DNS, contraintes de zones et quotas.
- Azure : subscriptions, vNet et subnets, permissions et cloud identity.
- Google Cloud : projects, service accounts, VPC, Cloud DNS et quotas.
- vSphere : vCenter/datastores, réseau virtuel, templates et stockage supporté.
- Bare metal : BMC, boot ISO/PXE, DHCP ou IP statique, provisioning network, load balancers et DNS.

Les *mêmes mots* (nœud, machine, VIP, certificat) ne correspondent pas toujours aux mêmes responsabilités opérationnelles.

### 3.2 IPI ne signifie pas « le fournisseur s'occupe de tout »

L'installateur peut provisionner des Machines ou des composants sur certaines plateformes, mais le client reste responsable des comptes, permissions, réseau d'entreprise, politiques de sécurité, supervision des dépendances, décisions de résilience et coûts.

Pour UPI, la séparation est plus explicite : l'installateur OpenShift ne crée pas les mêmes objets provider et peut supposer l'existence de DNS, LB et bootstrap hosts préparés manuellement.

## 4. Cas disconnected et registre miroir

Le mode disconnected n'est pas simplement « couper Internet » :
1. identifier version exacte d'OCP et images de release requises;
2. disposer d'une machine de préparation connectée lorsque nécessaire;
3. mirrorer les images/metadata et les catalogues d'Operators choisis;
4. prévoir registry miroir et stockage;
5. configurer confiance CA, DNS et credentials;
6. vérifier la visibilité du registre depuis les hôtes au moment du bootstrap;
7. conserver une procédure documentée de mise à jour ultérieure.

Un cluster qui démarre mais ne peut plus tirer ses images de base n'est pas opérationnel. Les matrices de compatibilité et les supports de media installer dépendent de la version.

## 5. Grille de décision d'architecture

Ne pas choisir IPI/UPI uniquement parce que l'équipe est « DevOps ». La décision doit être étayée :

| Dimension | Question à documenter | Preuve ou entrée |
|---|---|---|
| Disponibilité | Panne d'hôte/zone admise ou non ? | RTO/RPO, contrats métier |
| Provider | Méthodes réellement supportées sur version 4.22 ? | Matrice installation Red Hat |
| Capacité | Baseline control plane, workloads et marge de maintenance ? | Sizing, requests, croissance |
| DNS et LB | Qui fournit et gère la résolution/API/VIP/Ingress ? | RACI et plan réseau |
| Sécurité | Qui détient pull secret, PKI, accès admin, provider roles ? | Matrice responsabilités |
| Disconnected | Quelles images, registries, mises à jour offline ? | Inventory release et catalogues |
| Storage | CSI et backend disponibles dès Day-1 ? | Matrice drivers et support |
| Économie | Coûts d'hébergement, licence, énergie et réserve ? | Estimation traçable |
| Cycle de vie | Upgrade, replacement et PRA supportés ? | Runbook et guide provider |
| Exploitation | Qui exploite après départ de l'installateur ? | RACI, monitoring, support N3 |

## 6. Étude de cas — SI de banque à trois domaines de panne

La banque veut héberger des APIs internes critiques et un canal de paiement. Une maquette CRC peut démontrer que la chaîne GitOps crée des objets, que les webhooks sont configurés et que les Pods passent Ready. **Elle ne démontre pas** que la banque survivra à la perte d'un hyperviseur ou d'une zone.

Une topologie cible doit répondre à :
- indépendance des domaines physiques des membres etcd;
- nombre de workers nécessaires lors d'une maintenance;
- disponibilité du LB API et de la PKI;
- répartition des replicas métiers;
- CSI compatible et sauvegarde/restauration vérifiables;
- circuit d'accès du personnel N3 et responsabilités d'exploitation.

La preuve attendue est un protocole de validation sur un environnement représentatif. Le présent chapitre ne revendique pas une qualification HA.

## 7. Questions d'architecte

1. Quelles distinctions entre une topologie et une méthode d'installation ?
2. Pourquoi CRC et SNO ne prouvent-ils pas une HA multinœud ?
3. Pourquoi « trois masters » ne signifie pas « trois domaines de panne » ?
4. Quels composants une installation UPI exige-t-elle souvent de préparer ?
5. Un cluster dit « disconnected » peut-il avoir des dépendances non déclarées à un registre public ?
6. Quelle information consulter avant de proposer IPI sur un provider donné ?
7. Quels critères refuseraient le choix d'un SNO pour des paiements critiques ?

## Sources

- [Red Hat — Installation overview OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installation_overview/ocp-installation-overview)
- [Red Hat — Preparing to install SNO 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_a_single_node/preparing-to-install-sno)
- [Red Hat — Installing SNO 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_a_single_node/install-sno-installing-sno)
- [Red Hat — Installing on bare metal](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_bare_metal/index)
- [Red Hat — Agent-based Installer](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_an_on-premise_cluster_with_the_agent-based_installer/index)

**Aucune installation ni opération d'infrastructure n'a été lancée pour cette rédaction.**
