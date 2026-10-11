# V02-L06 — OLM Classic versus OLM v1 : contrat de livraison d'un Operator

**Mode : PAPER_LAB / DOCUMENTED_NOT_RUN. Aucune Subscription, ClusterExtension ou CRD réellement installée.**

## 1. Mise en situation

Une banque souhaite installer un Operator de routage de services sur un cluster OpenShift 4.22. La sélection du mécanisme dépend notamment des formats de bundles, du catalogue, des API présentes et de l'objectif de gouvernance.

Deux options **fictives** :

**Option A — OLM Classic** : un package \`sample-route-operator\` possède un CSV \`sample-route-operator.v1.4.0\`, un CatalogSource, un channel \`stable\`, une Subscription avec InstallPlanApproval Manual et un OperatorGroup prévu pour son namespace.

**Option B — OLM v1** : un package compatible avec le format \`registry+v1\` est exposé dans un ClusterCatalog. L'installation serait décrite par un ClusterExtension \`olm.operatorframework.io/v1\`, avec un ServiceAccount existant et droits minimum.

Le PDF n'affirme pas que ces deux options gèrent *le même* Operator ni qu'elles sont interchangeables. Le format d'un bundle et les capabilities du cluster conditionnent le choix.

## 2. Exercice E1 : retrouver l'autorité de chaque objet

| Ressource | Mécanisme | Rôle |
|---|---|---|
| ClusterVersion | CVO | Version du payload OpenShift |
| ClusterOperator | CVO / plateforme | Conditions d'un opérateur fondamental |
| CatalogSource | OLM Classic | Référence de catalogue |
| Subscription | OLM Classic | Package, channel, politique d'install |
| InstallPlan | OLM Classic | Plan d'install/upgrade |
| CSV | OLM Classic | Version/install strategy |
| OperatorGroup | OLM Classic | Portée de watch/installation |
| ClusterCatalog | OLM v1 | Source FBC et métadonnées |
| ClusterExtension | OLM v1 | Intention d'installation d'une extension |
| CustomResourceDefinition | API Kubernetes | Contrat de ressources personnalisées |

**Piège :** un ClusterOperator d'OpenShift ne s'upgrade pas en créant une Subscription vers une ancienne version de son contrôleur.

## 3. Exercice E2 : approbation manuelle

Une Subscription est définie avec \`installPlanApproval: Manual\`. Le catalogue contient un package plus récent, mais le nouveau CSV n'est pas installé. Faut-il déclarer OLM Degraded ?

**Corrigé :** pas sans identifier un échec. Un InstallPlan peut légitimement être en attente d'approbation. Vérifier son statut, ses ressources, le canal, la compatibilité et la décision de changement. Ne pas approuver un plan depuis une procédure de lecture seule.

## 4. Exercice E3 : ClusterExtension et verrouillage des versions

Le contrat OLM v1 \`ClusterExtension.spec.source.catalog\` accepte des canaux et une contrainte de version. Exemple **non déployable** :

~~~yaml
apiVersion: olm.operatorframework.io/v1
kind: ClusterExtension
metadata:
  name: example-database-operator
spec:
  namespace: demo-operators
  serviceAccount:
    name: extension-install-sa
  source:
    sourceType: Catalog
    catalog:
      packageName: example-database-operator
      channels: [stable]
      version: "1.2.3"
      upgradeConstraintPolicy: CatalogProvided
~~~

La version exacte \`1.2.3\` empêche normalement l'upgrade automatique hors de ce pin; la sélection du bundle demeure dépendante du package/catalogue. Red Hat documente que channels et version sont combinés par une logique ET. Les paramètres réels et la compatibilité doivent être contrôlés par le responsable de plateforme.

**Erreur à éviter :** mettre \`upgradeConstraintPolicy: SelfCertified\` pour contourner un graphe incompatible. Le modèle peut autoriser des upgrades/downgrades dangereux; une acceptation formelle et des tests seraient nécessaires.

## 5. Exercice E4 : CRD upgrade et conservation des données

Une version d'Operator ajoute v1beta1, puis désactive v1alpha1. Les équipes GitOps publient encore des CR en v1alpha1.

**Conséquence :** les déploiements GitOps utilisant l'ancienne API peuvent échouer, même si l'Operator est déclaré Installed ou si son CSV est Succeeded.

**Corrigé :** inventorier les CR existantes, les versions servies, la version de stockage, les clients et les webhooks; maintenir une fenêtre de double served et migrer les objets avant suppression de v1alpha1. L'exercice [V02-L04](v02-04-crd-conversion-offline.md) présente la version offline du contrat de conversion.

## 6. Diagnostic read-only conditionnel

Sur un cluster autorisé :

~~~bash
# OLM Classic
oc -n openshift-marketplace get catalogsources
oc -n NAMESPACE get subscriptions,installplans,csv,operatorgroups

# OLM v1
oc get clustercatalogs.olm.operatorframework.io
oc get clusterextensions.olm.operatorframework.io
~~~

Ne pas interpréter un ResourceNotFound ou un RBAC Forbidden sans distinguer capability absente, namespace incorrect et droits insuffisants. Les fonctionnalités OLM v1 sont activées par défaut depuis OCP 4.18 dans les configurations documentées, mais les capabilities réelles et les ressources disponibles de chaque cluster doivent être vérifiées.

## 7. Matrice de revue avant production

| Gate | Source de preuve |
|---|---|
| Compatibilité avec OCP cible | Support de package et propriétés de compatibilité |
| Catalogue | Origine, digest, Serving, cadence de mise à jour |
| Installer permissions | ServiceAccount et RBAC minimal |
| Webhooks | Certificats, disponibilité et plan de reprise |
| CRD | served/storage, storedVersions, clients hérités |
| Images | Digests, provenance, scan et signatures selon politique |
| Rollback | Stratégie compatible avec migrations de CRD et données |
| Métier | SLO mesurés par tests représentatifs et non seul Installed |

## 8. Limite de preuve

Ce cas sur papier permet de vérifier les **frontières et pièges du lifecycle OLM**. Il n'exécute pas d'InstallPlan, de Catalogd, de registry pull ou de ClusterExtension. Aucun résultat RUNTIME_PROVEN ne peut en découler.

Sources : [Red Hat 4.22 — OLM Classic](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/understanding-operators) ; [Architecture OLM v1](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/extensions/architecture) ; [API ClusterExtension v1](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operatorhub_apis/clusterextension-olm-operatorframework-io-v1).
