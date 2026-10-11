# 12 — Configuration, Secrets, quotas et multi-tenancy : le contrat d'une plateforme

**Volume 01 — édition 1.0 de contenu · Niveau : Platform Engineer / Architecte Solutions**  
**Portée : Kubernetes et OpenShift 4.22 · Type : principes vérifiables et architectures de référence**

## 1. Le problème à résoudre

Une plateforme multitenant ne se définit pas par le nombre de namespaces. Elle se définit par l'ensemble des frontières de responsabilité, d'identité, de consommation, d'accès réseau et de gestion du cycle de vie qu'elle rend explicites.

Une application a besoin d'une configuration qui évolue, de secrets protégés, d'une identité de machine, de ressources limitées et d'une topologie réseau autorisée. Mélanger toutes ces responsabilités dans un unique manifeste Deployment rend les changements difficiles à auditer et multiplie les accès privilégiés.

## 2. ConfigMap versus Secret

| Objet | Contenu attendu | Risque | Règle |
|---|---|---|---|
| ConfigMap | Configuration non confidentielle | Incohérence versions, mauvais format | Versionner et valider le schéma |
| Secret | Mots de passe, tokens et certificats suivant leur usage | Exposition et rotation | Ne jamais exporter les valeurs dans le livre ni dans Git en clair |
| ServiceAccount | Identité Kubernetes d'un Pod | Privilèges API excessifs | Un compte par responsabilité et permissions minimales |
| Namespace | Frontière d'organisation des ressources namespacées | Fausse croyance d'isolation absolue | Combiner RBAC, SCC, policy, quotas |
| ResourceQuota | Budget maximal agrégé d'un namespace | Bloque des créations valides en apparence | Inclure overhead et scénarios de pointe |
| LimitRange | Politiques de valeurs par défaut/min/max | Requests/limits implicites inattendus | Expliquer le contrat de ressources |

**Important :** un Kubernetes Secret n'est pas chiffré en soi uniquement parce que son objet est nommé Secret. L'encodage base64 du manifeste YAML n'est pas du chiffrement. La protection au repos dépend de la configuration du control plane et du système de stockage des données API; l'accès dépend de RBAC et du cycle de vie des identités.

### 2.1 Exemple de configuration pédagogique

~~~yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-reader-config
  namespace: training-v01
data:
  HTTP_PORT: "8080"
  TIMEOUT_MS: "1500"
  FEATURE_READ_ONLY: "true"
~~~

Il n'y a pas de secrets dans cette ConfigMap. Le \`TIMEOUT_MS\` doit être interprété par l'application; Kubernetes ne lui attribue pas une sémantique de délai. En exploitation, valider les contraintes telles que 100 ms <= timeout <= 10 s selon le contrat technique, et documenter les effets d'un changement.

### 2.2 Consommation par environnement

Les configurations peuvent être injectées en variables d'environnement ou montées comme fichiers. Les variables d'environnement **ne se mettent pas automatiquement à jour dans le processus** lorsque la ConfigMap/Secret change. Les volumes projetés peuvent mettre à jour certains fichiers avec un délai; cette dynamique dépend du montage et de la façon dont l'application lit le fichier. Un montage utilisant \`subPath\` présente des limitations de mise à jour à connaître.

Architecture de mise à jour :
1. nouvelle valeur approuvée;
2. validation du schéma;
3. révision de l'objet;
4. déploiement/reload contrôlé selon contrat applicatif;
5. observation de l'application sur nouvelle génération;
6. rollback possible de la configuration **sans supposer** rollback automatique des données.

### 2.3 Secret : règles de bout en bout

Ne jamais stocker un token réel dans un exemple, une capture ou une Pull Request publique. Les mécanismes de livraison envisageables incluent un gestionnaire de secrets, un Operator de secrets externes, un coffre central, ou un processus sécurisé de provisioning approuvé. Le choix dépend des politiques du système d'information et des composants supportés.

Questions à résoudre :
- qui émet, peut lire et révoquer le secret ?
- quel est le TTL et comment la rotation est-elle déclenchée ?
- la rotation exige-t-elle redémarrage ou reload ?
- comment garantir que le nouveau secret et l'ancien se chevauchent durant la transition ?
- où les secrets pourraient-ils être exposés par logs, Events, tableaux de bord, CI ou support bundle ?
- comment rétablir un cluster sans restaurer des secrets périmés ou révoqués ?

La sûreté des secrets dépend de **leur cycle de vie**, pas seulement de leur mode de stockage.

## 3. Authentification API et identité applicative

Il faut distinguer trois identités :

- **Utilisateur humain** : connecté à l'API par un fournisseur d'identité selon l'intégration du cluster.
- **ServiceAccount** : identité de workload pour les opérations Kubernetes qui sont effectivement requises.
- **Identité métier** : claims OIDC ou contexte de délégation traité par l'application, avec ses propres autorisations sur les données.

Le fait qu'un Pod dispose d'un ServiceAccount n'implique pas qu'il ait besoin d'appeler l'API Kubernetes. Désactiver l'auto-montage du token API lorsqu'il n'est pas nécessaire réduit l'exposition de credentials dans le processus.

Exemple illustratif :

~~~yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: payment-reader
  namespace: training-v01
automountServiceAccountToken: false
~~~

Cette option peut être surchargée à la configuration du Pod; contrôler le résultat réel. L'absence de token Kubernetes n'empêche pas l'application d'utiliser une authentification HTTP/OIDC séparée vers ses dépendances métier.

## 4. RBAC : rôle, binding, portée et audit

Un Role déclare des opérations sur des ressources namespacées; un ClusterRole permet également des permissions cluster-scoped ou des règles réutilisables. Un RoleBinding attribue des droits dans un namespace, éventuellement en référant un ClusterRole. Un ClusterRoleBinding accorde ces permissions au niveau cluster.

### Exemple de droit de lecture ciblé

~~~yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-reader
  namespace: training-v01
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch"]
~~~

**Règle essentielle :** les ressources secrets ne figurent pas dans ce Role. Ne pas créer un \`ClusterRoleBinding\` simplement parce qu'un \`RoleBinding\` ne semble pas suffire : chercher d'abord une erreur de namespace, groupe API ou identité.

Contrôles read-only :

~~~bash
oc -n NAMESPACE get roles,rolebindings
oc -n NAMESPACE get serviceaccounts
oc auth can-i get deployments -n NAMESPACE
oc auth can-i get secrets -n NAMESPACE
~~~

Ces commandes ne révèlent pas de valeur de Secret. Ne pas effectuer \`oc get secret -o yaml\` dans un laboratoire public.

## 5. Quotas et demandes de ressources

Exemple pédagogique de quota **à ne pas appliquer sur un namespace partagé** :

~~~yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-budget
  namespace: training-v01
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "12"
~~~

Calcul préflight :
- 6 Pods à 200m CPU de request = 1,2 CPU;
- 6 Pods à 512Mi request = 3 Gi;
- on reste sous les quotas ci-dessus **pour ces Pods seulement**;
- d'autres workloads, Jobs et overhead éventuel peuvent rendre la demande non admissible;
- un Pod sans request ou limit peut être refusé selon la politique de quotas/LimitRange.

Un quota ne garantit ni un scheduling réussi ni la disponibilité de CPU physique. Il borne l'utilisation des ressources déclarées/consommées selon les catégories suivies, mais le placement dépend de l'allocatable des nœuds et des contraintes topologiques.

## 6. Le faux isolement d'un namespace

Deux équipes séparées par des namespaces restent sur un cluster partagé et peuvent partager :
- control plane et etcd;
- ingress, DNS et réseau du cluster;
- certains nœuds, OS, runtime et pools de stockage;
- capacité et domaines de panne;
- opérations administrateur cluster et politiques globales.

Par conséquent, **namespace != tenant matériellement isolé**. Pour des besoins de souveraineté, de confidentialité ou de blast radius strict, la décision peut imposer des clusters dédiés, souscriptions séparées, nœuds dédiés ou contrôles supplémentaires. La preuve doit être liée à l'exigence métier et non à la présence d'un label.

## 7. Exemple de contrat d'un « tenant » plateforme

| Capacité | Contrat de service plateforme | Preuve de réception |
|---|---|---|
| Provisionnement | Namespace et identities créés via demande approuvée | Namespace, rôles et bindings lisibles |
| Delivery | Déploiement via GitOps autorisé | Commit et revision audités |
| Sécurité | SCC, image policy, NetworkPolicy | Tests négatifs / admission |
| Ressources | Quota, LimitRange et allocation documentés | Rejet contrôlé quand dépassés |
| Réseau | Flux prévus, DNS, egress et ingress | Tests connectivité positifs/négatifs |
| Secrets | Rotation et révocation gérées | Simulation de rotation sans exposition |
| Monitoring | SLI technique et propriétaire métier | Dashboards, alertes et corrélation |
| Incident | Runbook et escalade connue | Drill avec horodatage |

Un Golden Path peut automatiser ces étapes, mais le portail IDP n'est pas l'autorité finale de sécurité; les contrôles sont exécutés côté plateforme/API.

## 8. Diagnostic en lecture seule

~~~bash
oc -n NAMESPACE get resourcequota,limitrange
oc -n NAMESPACE describe resourcequota
oc -n NAMESPACE get serviceaccounts
oc -n NAMESPACE get rolebindings
oc -n NAMESPACE get networkpolicies
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

Approche : si un Pod est refusé pour une request non conforme, observer quota et LimitRange; si RBAC répond « yes » mais l'admission refuse, regarder SCC/PSA; si le Pod tourne mais n'accède pas à la base, regarder identité métier, certificats et réseau. Ne jamais corriger toutes les dimensions simultanément.

## 9. Décisions d'architecture à documenter

1. Le namespace est-il la bonne limite de séparation ou faut-il un cluster ?
2. Qui peut modifier les policies et autoriser les exceptions ?
3. Le service account doit-il contacter l'API Kubernetes ?
4. Où sont gérés les secrets, sous quelle identité, avec quel audit ?
5. Quels composants déclenchent une rotation et combien de temps est-elle tolérée ?
6. Quelles sont les demandes CPU/RAM minimales mesurées en charge ?
7. Le risque d'un ResourceQuota atteint est-il traité par scaling, admission ou négociation ?
8. Comment reconstruire le tenant à partir de Git après suppression contrôlée ?

## Sources

- [Kubernetes — ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/)
- [Kubernetes — Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Kubernetes — Service Accounts](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [Kubernetes — RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes — Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)
- [Kubernetes — Limit Ranges](https://kubernetes.io/docs/concepts/policy/limit-range/)
- [Red Hat — OCP 4.22 Authentication and authorization](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/index)

**Limite** : exemples éducatifs, pas une politique déployée et approuvée dans un SI réel.
