# 04 — Cluster Version Operator, release image et gouvernance des mises à jour

**Volume 02 · DRAFT · OpenShift Container Platform 4.22 · Documentation officielle vérifiée.**  
**Aucune commande d'upgrade ni changement de channel n'est exécuté dans ce chapitre.**

## 1. Pourquoi CVO n'est pas un simple outil de rollout

Le **Cluster Version Operator (CVO)** pilote l'évolution des composants fondamentaux du cluster OpenShift. Il utilise une release image comme représentation d'un ensemble cohérent de composants et manifeste une version désirée via la ressource ClusterVersion. Les ClusterOperators gèrent leurs propres périmètres et publient leur état dans des objets ClusterOperator.

Un rollout de Deployment applicatif n'est pas un upgrade OCP. L'upgrade touche API, Operators, runtime, OS et dépendances de la plateforme et doit respecter un graphe de compatibilité.

~~~mermaid
flowchart TD
  OSUS[OpenShift Update Service / graphe] --> CVO[CVO]
  CV[ClusterVersion] --> CVO
  IMAGE[Release image signée] --> CVO
  CVO --> CO[Cluster Operators de base]
  CO --> API[API / Scheduler / etcd / réseau]
  CO --> MCO[Machine Config Operator]
  MCO --> RHCOS[RHCOS sur les nœuds]
~~~

Le schéma montre les responsabilités. Le processus réel applique des manifests ordonnés par niveaux de dépendance et peut exécuter plusieurs changements en parallèle sous contrôles de compatibilité.

## 2. Release image, digest et chaîne de confiance

La release image constitue le point de référence de la version cible. Le CVO obtient l'image cible et vérifie les propriétés d'intégrité/authenticité selon le mécanisme supporté. Un tag mutable de registre ne doit pas être assimilé à la preuve d'une version déployée.

Une revue d'upgrade doit enregistrer :
- version actuelle et cible, canal de recommandation;
- image de release et identifiant immuable;
- métadonnées du graphe et conditions de mise à jour;
- versions Kubernetes/RHCOS/CRI-O effectives;
- état des opérateurs et pools;
- historique et raison d'upgrade.

L'existence d'une version « plus récente » sur Internet ne prouve pas qu'elle est recommandée pour **ce cluster**.

## 3. ClusterVersion : désiré, historique, état observé

Les conditions les plus utiles ne sont pas interchangeables :

| Condition | Question | Ce qu'elle ne prouve pas |
|---|---|---|
| Available | Une version de la plateforme est-elle en service selon CVO ? | Toutes les transactions métier passent |
| Progressing | Le cluster converge-t-il vers une cible ? | Durée de fin garantie |
| Upgradeable | Certaines barrières bloquent-elles une mise à jour ? | Que le passage en production est sans risque |
| Failing | Le processus de gestion/version connaît-il un échec ? | Cause racine connue |
| RetrievedUpdates | Les recommandations de mise à jour ont-elles été récupérées ? | Connectivité vers tous les registres/bundles |

Red Hat documente aussi des conditions telles qu'Invalid; la liste et la sémantique précises restent liées à l'API/version concernée.

Inspecter sans modifier :

~~~bash
oc get clusterversion version -o yaml
oc get clusteroperators
oc adm upgrade
oc get machineconfigpools
~~~

Certaines de ces lectures peuvent exposer URL internes et détails de versions; expurger les sorties avant diffusion. L'invocation de \`oc adm upgrade\` **sans option de mutation** sert à afficher les recommandations; ne pas utiliser \`--to\`, \`--to-image\` ou \`--force\` dans un atelier.

## 4. Graphe OSUS et chemins de mise à jour

L'OpenShift Update Service fournit un graphe de versions et chemins envisageables. Ses recommandations peuvent tenir compte de contraintes spécifiques à certaines releases, canaux et architectures.

- **fast** : nouvelles versions GA publiées plus tôt dans le canal.
- **stable** : disponibilité après délai d'observation.
- **candidate** : versions candidates selon leur cycle.
- **eus** : choix liés aux politiques de support étendu, selon disponibilité.

Le channel est un mécanisme de recommandation et d'orientation des updates, **pas** une permission automatique de forcer une version arbitraire. Red Hat indique qu'un rollback du cluster vers une version antérieure n'est pas supporté; il faut distinguer un rollback applicatif GitOps d'une restauration de control plane selon procédure exceptionnelle.

## 5. Manifestes, runlevels et dépendances

La release image contient des manifestes nécessaires à la cible. La logique d'upgrade doit notamment respecter la création d'une CRD avant ses CRs et l'ordre approprié entre différents ClusterOperators. Red Hat décrit des runlevels dans les noms de manifests et un ordonnancement qui respecte les dépendances.

Cela explique pourquoi le déploiement d'une nouvelle image OS n'est pas la première ni la seule action d'un upgrade. Une stratégie personnalisée qui applique des manifests du control plane manuellement court-circuite la chaîne de support.

## 6. CVO et OLM : frontières de responsabilités

Le CVO gère les **ClusterOperators faisant partie du payload de plateforme**. Les add-on Operators installés par OLM suivent une autre logique de cycle de vie.

| Cluster Operator | Add-on Operator OLM |
|---|---|
| Typiquement installé avec le cluster | Installé pour une fonctionnalité additionnelle |
| Généralement piloté via la version du payload OCP | Catalogues, subscriptions et modèles OLM selon génération |
| Statut cluster dans ClusterOperator | CSV/conditions ou mécanismes spécifiques selon version OLM |
| Upgrade lié au lifecycle de la plateforme | Compatibilité à valider séparément |

Ne pas supposer que tous les Operators de l'écosystème utilisent les mêmes API OLM ni qu'ils peuvent tous être mis à jour indépendamment de la version OCP.

## 7. Préflight d'upgrade N3

Une mise à jour n'est pas un remède générique à un cluster dégradé. Un préflight sérieux doit vérifier :

1. santé ClusterVersion et ClusterOperators;
2. MCP Updated/Updating/Degraded et versions souhaitées vs actuelles;
3. incidents en cours, alertes critiques et pression ressources;
4. quorum etcd et existence de sauvegardes compatibles selon guide;
5. état stockage/CSI, réseau, ingress, DNS, identity, registry;
6. capacité disponible pour cordon/drain et surge de Pods;
7. PDB susceptibles de bloquer les drains;
8. compatibilité des CRDs/Operators additionnels;
9. chemins de mise à jour recommandés, release notes et changes connus;
10. fenêtre, responsables, observabilité et critères d'arrêt.

La vérification s'effectue dans un environnement autorisé et les preuves sensibles restent privées.

## 8. Scénario d'incident : CVO Progressing et MCP Degraded

Considérons un cluster fictif présentant CVO Progressing=True et un MCP Degraded=True. Il ne faut pas conclure à un problème CVO isolé : le MCO peut signaler l'impossibilité de conduire un nœud au rendered config cible.

Triage :
- examiner la condition du MCP et le nœud précis concerné;
- comparer currentConfig et desiredConfig via annotations/objets supportés, **sans modification**;
- vérifier statut du nœud, drain, PDB et événements;
- relever version et image souhaitée;
- consulter runbook officiel avant toute intervention.

Débloquer une mise à jour en supprimant une ressource de plateforme ou forçant un état « Updated » serait une falsification de preuve et un risque majeur.

## 9. Architecture bancaire : gouvernance de la mise à jour

Une banque doit disposer d'une stratégie de changement qui distingue :
- environnements de développement, préproduction et production;
- validation des chemins et supports de versions;
- segmentation de domaines de panne;
- périodes de forte charge et fenêtres de maintenance;
- instances critiques : paiement, MQ, IAM, bases, décision;
- critères de non-régression : latences et taux d'erreur métiers, pas seulement Pods Ready;
- plan de communication, décision d'arrêt et gestion de support Red Hat.

Un test de mise à jour sur CRC atteste au mieux du mécanisme dans cette topologie; il ne démontre ni tolérance zonale ni continuité de service d'un cluster multinœud.

## 10. Questions de soutenance

1. Pourquoi une release image est-elle centrale dans le modèle d'upgrade ?
2. Quelle différence entre CVO et un opérateur add-on OLM ?
3. Quelle différence entre Recommended update et capacité de production ?
4. Que veut dire Progressing=True/Upgradeable=False ?
5. Comment expliquer un blocage de MCP pendant un upgrade ?
6. Pourquoi le rollback de Deployment n'est-il pas un downgrade OpenShift ?
7. Quels contrôles essentiels doivent précéder une fenêtre d'upgrade ?

## Sources

- [Red Hat — Comprendre les mises à jour OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/understanding-openshift-updates-1)
- [Red Hat — Préparation aux updates OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/preparing-to-update-a-cluster)
- [Red Hat — Architecture / Operators](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — Cluster Operators reference](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operator-reference)

**Statut de preuve :** documentaire; aucun upgrade ou changement de cluster pendant la rédaction.


## 11. Méthode de qualification des chemins de mise à jour

Un graphe de releases ne donne pas une permission de production sans préflight. Le Comité de changement doit distinguer quatre notions : une release publiée, un chemin recommandé depuis la version actuelle, une mise à jour réellement supportée pour la configuration du cluster, et une fenêtre approuvée après essais sur les dépendances applicatives.

### 11.1 Les cinq dépendances à examiner

| Dépendance | Question de préflight | Risque |
|---|---|---|
| API / etcd | Version, quorum, latence, sauvegarde compatible ? | API inaccessible, perte d'état |
| MCO / RHCOS | Pools Ready, marge pendant drain/reboot ? | Workloads non placés |
| Réseau / identité | DNS, ingress, CA et tokens compatibles ? | Perte de connectivité |
| CSI / stockage | Driver compatible, snapshots et restore prévus ? | Données inaccessibles |
| Add-on Operators | CRD, catalogues, versions supportées ? | Boucle de réconciliation dégradée |

L'état Available=True d'un ClusterOperator est une observation utile, mais ne prouve pas que les transactions métiers ont respecté leur SLO pendant le changement.

### 11.2 Les métriques de la mise à jour

L'équipe de plateforme doit enregistrer les timestamps de Progressing, l'état des ClusterOperators, le délai de convergence des MachineConfigPools, les interruptions d'API et la durée des Pods non Ready. Le métier mesure indépendamment les requêtes réussies et les latences p95/p99.

Une mise à jour qui se termine avec tous les Operators Healthy peut quand même avoir dépassé le budget d'indisponibilité métier pendant la fenêtre.

## 12. Enquête sur un CVO Progressing prolongé

Scénario fictif : un worker ne converge pas vers la nouvelle configuration et CVO reste Progressing. Le diagnostic N3 doit construire une chronologie.

1. Identifier la version désirée et l'historique de ClusterVersion.
2. Lister les ClusterOperators dont les Conditions sont non nominales et leurs raisons.
3. Examiner les MCP et le nombre exact de machines Updated, Updating et Degraded.
4. Observer les Nodes et leur domaine de panne.
5. Vérifier les PDB pouvant empêcher le drain et les ressources nécessaires au replacement.
6. Contrôler les compatibilités des add-ons et des API utilisées.
7. Établir l'effet sur les transactions métier avec les observables SLI.
8. Décider une remédiation seulement via un runbook supporté et une autorité de changement.

Le simple fait de connaître le nom du ClusterOperator en difficulté ne confirme pas la cause. Pour une panne de nœud, la raison peut être un stockage local, un service systemd, un registre inaccessible ou une configuration MCO invalidée.

### 12.1 Ce qui n'est pas un rollback supporté

La documentation OpenShift 4.22 ne prend pas en charge un retour ordinaire à la version précédente du cluster. La restauration etcd est une procédure exceptionnelle, potentiellement destructrice et n'est pas destinée à être utilisée comme mécanisme de rollback de mise à jour. <Voir la référence officielle en fin de chapitre.>

Un revert Git sur une application ne remet pas CRI-O, RHCOS ou les APIs Kubernetes à une ancienne version.

## 13. Read-only : préserver les traces

Commandes non mutatrices, sous réserve de droits :

~~~bash
oc get clusterversion version -o yaml
oc get clusteroperators
oc get machineconfigpools
oc get nodes -o wide
oc get poddisruptionbudgets -A
oc adm upgrade
~~~

Ces commandes ne sont pas un protocole de restauration; elles servent au préflight et à la classification d'un incident.

## 14. ADR de gouvernance pour production bancaire

**Décision de référence :** valider l'upgrade par phases (environnement de test, préproduction, production), avec release image immuable et preuve du chemin de mise à jour supporté. Exiger une revue des Operators add-on, du stockage, du réseau, de la capacité et des contrôles métier avant la fenêtre.

**Critère d'acceptation :** changement traçable, ClusterOperators et MCP convergés, absence de nouveaux incidents graves, mesures SLO métier acceptables sur une durée approuvée.

**Risque résiduel :** une incompatibilité rare peut n'apparaître qu'avec une charge/une topologie propre à la production. Les protocoles de surveillance et d'escalade doivent donc rester actifs après la fin de CVO Progressing.

## Références spécifiques

- [Red Hat OCP 4.22 — Preparing to update a cluster](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/preparing-to-update-a-cluster)
- [Red Hat OCP 4.22 — Performing a cluster update](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/updating-cluster-cli)
- [Red Hat OCP 4.22 — Day-2 and worker node batching](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/postinstallation_configuration/day-2-operations-for-openshift-container-platform-clusters)
