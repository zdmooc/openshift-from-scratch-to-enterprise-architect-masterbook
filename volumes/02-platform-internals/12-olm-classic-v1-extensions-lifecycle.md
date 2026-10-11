# 12 — OLM Classic et OLM v1 : installation, versionnement et cycle de vie des Operators

**Volume 02 · Premier manuscrit technique · OCP 4.22 · PUBLIC_VERIFIED pour les concepts documentés.**  
**But : différencier les modèles de gestion d'extensions réellement décrits pour cette version, sans installer d'Operator sur le CRC.**

## 1. Trois Operators différents sous le même nom générique

La plateforme OpenShift 4.22 emploie le mot *Operator* pour plusieurs responsabilités :

1. **ClusterOperators du payload** : composants fondamentaux pilotés dans le cycle de version du cluster, avec CVO/ClusterVersion et statut ClusterOperator.
2. **Operators additionnels installés via OLM Classic** : découverte par CatalogSource, dépendances résolues et cycle Subscription/InstallPlan/CSV.
3. **Extensions gérées via OLM v1** : architecture Operator Controller + catalogd avec API ClusterCatalog / ClusterExtension.

Il est incorrect de dire que « tous les Operators OpenShift sont installés par OLM » ou qu'un ClusterOperator du control plane se met à jour simplement par une Subscription. Le CVO et OLM sont **des autorités de cycle de vie distinctes**. La qualification d'un add-on dépend de sa version, ses API, son mécanisme d'installation et sa compatibilité avec OCP.

## 2. OLM Classic : la chaîne complète

Les ressources clés sont :

| Ressource | Portée typique | Fonction |
|---|---|---|
| CatalogSource | Namespace, par exemple openshift-marketplace | Expose des packages/bundles pour découverte |
| OperatorGroup | Namespace | Détermine le périmètre de watch/installation d'Operators |
| Subscription | Namespace | Suit un package, channel, source et politique d'upgrade |
| InstallPlan | Namespace | Plan d'installation/résolution à approuver ou appliquer |
| ClusterServiceVersion | Namespace | Représente une version d'Operator, RBAC et APIs offertes/requises |
| CRD | Cluster | Déclare les API types de l'Operator |
| CR | Dépend de la CRD | Intention de l'utilisateur consommant ces API |

~~~mermaid
flowchart TD
  C[CatalogSource] --> SUB[Subscription]
  OG[OperatorGroup] --> SUB
  SUB --> IP[InstallPlan]
  IP --> CSV[ClusterServiceVersion]
  CSV --> OP[Operator Deployment]
  CSV --> CRD[CRD / APIs]
  CRD --> CR[Custom Resources]
  OP --> CR
~~~

Il s'agit d'un flux logique. Les dépendances et l'ordre détaillé varient selon package, CSV et résolution du graphe d'upgrade.

### 2.1 Un bundle n'est pas un conteneur qui exécute l'Operator

Un **bundle image** est une image OCI non exécutable contenant metadata et manifests de version (dont un CSV et les CRDs possédées applicables). L'image **Operator controller** est un autre artefact. Le catalogue indexe ces bundles via un **File-Based Catalog (FBC)** ou une représentation adaptée.

Un pipeline de release responsable doit lier :
- digest de l'image du contrôleur ;
- bundle contenant les manifests/CSV/permissions ;
- package et channel ;
- image/digest du catalogue ;
- exigences de la version OCP et des API ;
- procédures de migration des CRD/CR ;
- contrôle des vulnérabilités, signatures et licence.

**Ne pas confondre** la publication du bundle et le déploiement opérationnel de l'Operator.

### 2.2 Subscription et InstallPlan

Exemple documentaire destiné à un catalogue fictif, non applicable :

~~~yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: example-operator
  namespace: training-operators
spec:
  channel: stable
  installPlanApproval: Manual
  name: example-operator
  source: training-catalog
  sourceNamespace: openshift-marketplace
~~~

L'approbation **Manual** signifie que certaines installations/mises à jour exigent une approbation d'InstallPlan. Cela ne garantit pas une validation fonctionnelle de l'Operator et ne remplace pas un protocole de compatibilité. Le package, channel et source ne sont pas des ressources réelles de cet ouvrage.

La politique **Automatic** réduit les étapes humaines mais peut introduire un changement non testé si les channels avancent et si la gouvernance ne contrôle pas le catalogue.

### 2.3 Scope via OperatorGroup

Un OperatorGroup gère les namespaces que peuvent surveiller certains Operators OLM Classic. Une cohabitation d'Operators et des interactions de ownership peuvent créer des conflits. L'installation d'un Operator très privilégié dans un namespace « application » n'est pas une garantie d'isolation des droits : ses RBAC/CRDs peuvent être cluster-scoped.

Il faut examiner l'install mode supporté par le CSV, les namespaces cibles, les CRDs déjà possédées et les autres OperatorGroups.

## 3. OLM v1 : nouvelle architecture, nouveau contrat

OpenShift 4.22 documente également **OLM v1**, dont les deux composants principaux sont :

- **catalogd** : récupère/décompresse des File-Based Catalogs et rend leurs métadonnées disponibles.
- **Operator Controller** : résout et installe des extensions à partir des métadonnées et de la ressource API correspondante.

La ressource **ClusterCatalog** définit un catalogue v1 et **ClusterExtension** décrit une extension à installer. Contrairement à Subscription+OperatorGroup namespace-scoped, **ClusterExtension est cluster-scoped** en OLM v1, même si le contenu de la spec peut désigner un namespace d'installation.

~~~mermaid
flowchart LR
  REG[Image FBC en registry] --> CAT[ClusterCatalog]
  CAT --> CATALOGD[catalogd]
  CATALOGD --> CTRL[Operator Controller]
  EXT[ClusterExtension] --> CTRL
  CTRL --> INST[Operator/extension]
~~~

### 3.1 Ne pas transposer les noms Classic dans OLM v1

| Question | OLM Classic | OLM v1 |
|---|---|---|
| Déclaration d'installation | Subscription | ClusterExtension |
| Catalogue | CatalogSource | ClusterCatalog |
| Service de métadonnées | Operator Registry / catalog | catalogd |
| Résolution et install | OLM Classic / InstallPlan/CSV | Operator Controller / modèle d'extension |
| Définition de scope | OperatorGroup / installModes | ClusterExtension + configuration propre à l'extension |
| Portée de l'objet principal | Namespaced (selon CR) | ClusterExtension cluster-scoped |

**Attention :** cela ne prouve pas que toutes les extensions et tous les mécanismes d'upgrade de Classic sont pris en charge à l'identique en v1. Les fonctionnalités et restrictions supportées évoluent. Vérifier le guide **Extensions 4.22** et les ressources effectivement disponibles sur le cluster.

### 3.2 Exemple de ClusterExtension — forme documentaire, non déployable

~~~yaml
apiVersion: olm.operatorframework.io/v1
kind: ClusterExtension
metadata:
  name: example-platform-extension
spec:
  namespace: training-operators
  serviceAccount:
    name: extension-installer
  source:
    sourceType: Catalog
    catalog:
      packageName: example-extension
      channels:
      - stable
      version: "1.0.0"
~~~

Ce manifest exprime un **modèle**, pas une configuration validée sur un cluster. Les packages, versions, service accounts et catalogues sont fictifs. Des champs/configurations supplémentaires et des restrictions peuvent s'appliquer au bundle cible et à la version exacte.

### 3.3 Évolution d'un catalogue et risque de supply chain

Un FBC publié sous un tag mutable peut changer sans modification visible du YAML de l'extension. Il faut :
- identifier source et digest du catalogue;
- contrôler la provenance des bundles et images d'Operator;
- déterminer la politique de polling des catalogues;
- distinguer les mises à jour de catalogues Red Hat de celles des **catalogues personnalisés** ;
- conserver une matrice de versions supportées;
- valider les nouveaux champs de CRD et la conversion avant d'activer l'upgrade.

La documentation 4.22 indique que CVO peut ajuster automatiquement certains tags de CatalogSources Red Hat fournis par défaut lors d'upgrades cluster, **mais ne modifie pas automatiquement les catalogues personnalisés**.

## 4. Contrats d'upgrade : CRD et Operator doivent converger ensemble

Un Operator a souvent deux composants à mettre à jour :
- son exécutable (controller deployment, webhooks, permissions);
- le contrat API (CRDs, conversions et ressources existantes).

Scénario : une nouvelle version d'Operator supprime v1alpha1 de sa CRD alors qu'Argo CD déclare encore des CRs en v1alpha1. Même si le nouveau controller est Running, les applications GitOps échoueront à créer ou modifier leurs CRs.

Un upgrade robuste comprend :
1. inventaire des CRD et versions served/storage ;
2. identification des consommateurs (GitOps, scripts, API) ;
3. disponibilité et certificats des webhooks de conversion si nécessaires ;
4. lancement de versions compatibles en parallèle ;
5. migration des objets stockés, puis vérification de storedVersions ;
6. retrait des anciens clients ;
7. retrait final de l'ancienne version API ;
8. mesures de succès du controller et du métier.

Ne pas supprimer manuellement une CRD simplement pour « réinstaller proprement » un Operator : cela peut supprimer toutes les ressources custom du type, avec des répercussions graves.

## 5. Diagnostic OLM Classic en lecture seule

~~~bash
oc -n openshift-marketplace get catalogsources
oc -n NAMESPACE get subscriptions
oc -n NAMESPACE get installplans
oc -n NAMESPACE get csv
oc -n NAMESPACE get operatorgroups
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

Questions : le catalogue est-il accessible ? Le package/channel existe-t-il ? Un InstallPlan attend-il une approbation ? Le CSV est-il au statut prévu ? Une CRD ou un webhook est-il incompatible ? L'OperatorGroup correspond-il aux namespaces cibles ?

Un \`InstallPlan\` Pending manual n'est **pas nécessairement** une panne : c'est peut-être un gate de changement souhaité.

## 6. Diagnostic OLM v1 en lecture seule

~~~bash
oc get clustercatalogs.olm.operatorframework.io
oc get clusterextensions.olm.operatorframework.io
oc describe clusterextension.olm.operatorframework.io NOM_EXTENSION
oc get crds | grep -Ei 'olm|operators'
~~~

Ces ressources peuvent ne pas être installées, accessibles ou disponibles dans la configuration du cluster. La disponibilité exacte doit être confirmée sur OpenShift 4.22 et sur l'environnement ; un refus RBAC n'est pas un verdict d'indisponibilité.

## 7. Cas bancaires : Operator de base de données et gestion de change

Une banque utilise un Operator pour gérer un service PostgreSQL critique. Son upgrade ne doit pas être gouverné uniquement par la sortie \`csv Succeeded\` :

- l'Operator peut mettre à jour des CRDs et migrations de bases ;
- un webhook peut empêcher les créations de Pods ;
- les secrets d'accès peuvent évoluer ;
- la nouvelle version peut modifier une option par défaut ;
- les backups et restores doivent rester fonctionnels ;
- les SLI (erreur, latence, RPO/RTO) doivent être vérifiés avec des requêtes représentatives.

Choix d'architecture : maintenir une matrice **OCP × Operator × CRD × base × CSI** et exécuter une promotion par environnement, sous contrôle d'une politique de changement.

## 8. Tableau de comparaison CVO / OLM Classic / OLM v1

| Critère | CVO | OLM Classic | OLM v1 |
|---|---|---|---|
| Cible | Payload et Operators fondamentaux OCP | Operators additionnels | Extensions/Operators via nouveau modèle |
| Source d'intention | ClusterVersion | Subscription | ClusterExtension |
| Distribution | Release image OCP | Bundles, CatalogSource, CSV | FBC, ClusterCatalog, catalogd |
| Contrôle d'upgrade | Graphe OCP et compatibilité cluster | Channels, InstallPlans | Ressource de version et politique OLM v1 |
| Panne typique | Upgrade blocked par ClusterOperator | InstallPlan/CSV ou catalogue inaccessible | ClusterExtension/catalogd/Operator Controller |
| Preuve métier | À mesurer séparément | À mesurer séparément | À mesurer séparément |

Les trois mécanismes peuvent cohabiter mais ne doivent pas gérer la **même ressource ou version** sans contrat d'ownership. Le téléchargement d'une image de release ne garantit jamais, seul, l'intégrité d'une base de données métier.

## 9. Questions de soutenance

1. À quoi sert un bundle OCI non exécutable ?
2. Quelle différence entre CSV et CRD ?
3. Pourquoi un CSV Succeeded ne garantit-il pas Ready de toutes les CRs ?
4. Quel rôle joue un OperatorGroup et quelles limites de tenancy ?
5. Pourquoi une approbation Manual ne prouve-t-elle pas qu'un upgrade est sûr ?
6. Quelle différence entre CatalogSource et ClusterCatalog ?
7. Pourquoi ClusterExtension est-il cluster-scoped en OLM v1 ?
8. Quand un webhook de conversion peut-il rendre une migration dangereuse ?
9. Un ClusterOperator OCP se met-il à jour depuis une Subscription ?
10. Quelle preuve valide la compatibilité réelle d'un Operator avec OCP 4.22 ?

## Références officielles

- [Red Hat OCP 4.22 — Understanding Operators et OLM Classic](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/understanding-operators)
- [Red Hat OCP 4.22 — Extensions : architecture OLM v1](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/extensions/architecture)
- [Red Hat OCP 4.22 — Extensions : Catalogs](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/extensions/catalogs)
- [Red Hat OCP 4.22 — Operator user tasks](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/user-tasks)
- [Kubernetes — CRD versioning](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)

**Statut :** comparaison documentaire de deux modèles de gestion, non qualification d'un Operator client, sans installation runtime.
