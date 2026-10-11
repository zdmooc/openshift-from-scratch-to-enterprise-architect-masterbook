# 08 — Admission OpenShift : SCC, PSA, identité, Route et NetworkPolicy

**Volume 01 · Niveau : architecte plateforme / DevSecOps · Statut : EDITION_1_CONTENT_COMPLETE**  
**Périmètre documentaire : OpenShift Container Platform 4.22.**  
**Preuve : PUBLIC_VERIFIED pour les mécanismes publiés par Red Hat; les exemples et décisions de conception sont REFERENCE_ARCHITECTURE.**

## Objectifs pédagogiques

À l'issue du chapitre, savoir distinguer une erreur d'authentification API d'un refus RBAC, d'un rejet SCC/PSA, d'un problème de routage ou d'une NetworkPolicy; expliquer la différence edge/reencrypt/passthrough; concevoir un Pod compatible avec des contraintes de sécurité restrictives; examiner un chemin de trafic sans confondre la présence d'une Route avec la disponibilité métier.

## 1. Pourquoi la sécurité OpenShift ne se résume pas à RBAC

Une requête d'ajout de Pod ne réussit pas du seul fait qu'un utilisateur possède le verbe \`create\` sur la ressource \`pods\`. Il existe plusieurs barrières :

~~~mermaid
flowchart TD
  USER[Utilisateur ou contrôleur] --> AUTHN[Authentification API]
  AUTHN --> AUTHZ[Autorisation RBAC]
  AUTHZ --> MUT[SCC : sélection, éventuelles mutations et validation]
  MUT --> PSA[Pod Security Admission : profil namespace]
  PSA --> OTHER[Autres mécanismes d'admission configurés]
  OTHER --> ETCD[Persistance API]
  ETCD --> CTRL[Contrôleurs]
  CTRL --> KUBELET[kubelet / CRI-O]
  KUBELET --> RUNTIME[Exécution du Pod]
~~~

Ce diagramme est **logique**. L'ordre interne exact de l'admission n'est pas un contrat universel; pour SCC/PSA, la documentation OpenShift 4.22 décrit une vérification de SCC puis la validation PSA du Pod. Les composants d'admission configurés peuvent ajouter leurs propres conditions.

Le diagnostic doit localiser la barrière. Si \`oc auth can-i create pods\` donne « yes », cela ne prouve **pas** qu'un Pod privilégié, utilisant un volume hostPath, sera accepté. RBAC autorise la demande API; admission examine sa configuration.

## 2. SCC : le contrat de sécurité de l'exécution

Une **Security Context Constraint (SCC)** définit les propriétés qu'un Pod est autorisé à utiliser et, selon le champ, peut apporter des valeurs par défaut. Le contrôle concerne notamment :

- containers privilégiés, élévation de privilèges et Linux capabilities;
- user ID, SELinux, groupes de fichiers et groupes supplémentaires;
- utilisation des namespaces de l'hôte, hostNetwork et hostPath;
- types de volumes, profils seccomp et paramètres filesystem.

Red Hat déconseille de **modifier les SCC par défaut**; l'approche supportable est de créer une SCC personnalisée quand un besoin légitime l'impose, puis d'en gérer soigneusement les droits et la compatibilité. Une exception au moindre privilège doit être justifiée, tracée et testée. Ne pas modifier les étiquettes internes \`openshift.io/run-level\` des namespaces : elles changent le comportement de l'admission et sont réservées aux composants du cluster.

### 2.1 Pourquoi « chmod 777 + privileged » n'est pas un correctif

Un processus peut échouer sur l'écriture de \`/opt/app/cache\` à cause d'un UID non prévu par l'image, d'un volume en lecture seule, d'un contexte SELinux inadapté ou d'un filesystem root verrouillé. Accorder à l'ensemble du conteneur des privilèges puissants peut masquer le symptôme mais agrandir la surface d'attaque.

Chemin de correction :
1. relever l'erreur précise dans les Events et journaux d'application (en respectant la confidentialité);
2. vérifier \`runAsUser\` et les restrictions SCC réellement appliquées;
3. distinguer chemin système en lecture seule et données devant aller sur un volume spécifique;
4. adapter le contenu et les permissions de l'image lors de sa construction;
5. envisager une exception explicitement approuvée **uniquement** si le design l'exige.

### 2.2 Déduire l'UID effectif

Pour une application conçue pour OpenShift, il est souvent plus robuste de supporter un UID arbitraire que de dépendre d'un UID fixé dans le manifeste. Ne pas définir un \`runAsUser\` explicite sans vérifier la SCC et la politique de sécurité. L'UID réel du processus ne se déduit pas uniquement du fichier Dockerfile : l'admission et le runtime peuvent modifier sa valeur.

## 3. PSA et SCC : deux contrôles distincts

**Pod Security Admission (PSA)** applique les standards Pod Security Standards (PSS) aux namespaces avec les modes \`enforce\`, \`warn\`, \`audit\`. Les niveaux usuels sont \`privileged\`, \`baseline\` et \`restricted\`.

| Contrôle | Configuration principale | Effet |
|---|---|---|
| SCC | Ressource de cluster et autorisations de l'acteur/service account | Contrainte, validation et éventuellement mutation de sécurité du Pod |
| PSA enforce | Politique de sécurité du namespace | Peut rejeter des Pods non conformes au profil |
| PSA warn | Profil du namespace | Avertissement dans les réponses |
| PSA audit | Profil du namespace | Constat journalisé à l'audit |
| RBAC | Roles, ClusterRoles, bindings | Autorise ou refuse les verbes API |

L'admission **SCC n'est pas identique à PSA** et les deux doivent être satisfaites. La documentation Red Hat 4.22 décrit notamment l'application de valeurs par défaut via SCC, suivie de la validation SCC et du contrôle PSA. Les profils actifs varient selon le namespace et la configuration de la plateforme : ne pas présumer que tous les namespaces adoptent le même mode \`enforce\`.

### 3.1 Lecture seule : comprendre la politique sans la changer

~~~bash
oc -n NAMESPACE get namespace NAMESPACE -o yaml
oc -n NAMESPACE describe pod POD
oc get scc
oc auth can-i create pods -n NAMESPACE
oc -n NAMESPACE get serviceaccounts
~~~

Ces lectures requièrent des droits adaptés. Le nom \`NAMESPACE\` est un placeholder : il ne correspond pas à une ressource réelle. Les sorties peuvent contenir des informations d'infrastructure; ne pas les publier sans retrait des champs sensibles.

Ne **pas** résoudre un refus par \`oc adm policy add-scc-to-user ...\` sans analyse, approbation et revue RBAC.

## 4. Du Pod au client : Route, Service et EndpointSlice

Une Route OpenShift est une ressource déclarative qui décrit l'exposition d'un Service. Le routeur / Ingress Controller réalise le chemin de trafic. Le Service sélectionne des backends; les EndpointSlices décrivent les endpoints correspondants. La Route n'a pas le pouvoir de rendre Ready des Pods qui ne le sont pas.

~~~mermaid
flowchart LR
  CLIENT[Client HTTPS] --> DNS[DNS et Load Balancer]
  DNS --> ROUTER[Ingress Controller]
  ROUTER --> SERVICE[Service, targetPort]
  SERVICE --> EP[Endpoints éligibles]
  EP --> POD[Container HTTP]
~~~

Il s'agit d'une vue logique; les objets Service et EndpointSlice ne sont pas des proxys obligatoirement traversés physiquement. Le dataplane effectif dépend de la topologie réseau.

### 4.1 Terminaison TLS : trois choix avec des conséquences différentes

| Mode Route | Client → routeur | Routeur → backend | Conséquences |
|---|---|---|---|
| **edge** | HTTPS, TLS terminé au routeur | Généralement HTTP en clair | Simplicité; segment interne **non chiffré** |
| **reencrypt** | HTTPS, TLS terminé au routeur | Nouvelle connexion TLS vers backend | Vérifier certificat du backend / chaîne de confiance |
| **passthrough** | TLS bout en bout vers backend | Le routeur transmet le flux chiffré | Gestion TLS par le backend; routage fondé notamment sur SNI |

Exemple de choix : pour une consultation bancaire soumise à chiffrement du réseau interne, un simple Route **edge** ne remplit pas une exigence de chiffrement jusqu'au Pod. Une option **reencrypt** ou une autre architecture TLS peut être nécessaire selon contrat de sécurité, certificats et réseau. Un choix de terminaison ne remplace pas l'autorisation API.

### 4.2 Exemple explicatif : Route edge

~~~json
{
  "apiVersion": "route.openshift.io/v1",
  "kind": "Route",
  "metadata": {"name": "ledger-reader", "namespace": "workshop-v01"},
  "spec": {
    "host": "training.example.invalid",
    "to": {"kind": "Service", "name": "ledger-reader"},
    "port": {"targetPort": "http"},
    "tls": {"termination": "edge", "insecureEdgeTerminationPolicy": "Redirect"}
  }
}
~~~

\`training.example.invalid\` n'est pas un DNS utilisable : il empêche de faire passer un exemple pour un manifeste prêt à produire. Le JSON est accepté comme représentation d'objet Kubernetes, mais ne doit pas être appliqué tel quel.

## 5. Une NetworkPolicy ne remplace ni une Route ni un firewall externe

Les NetworkPolicies Kubernetes contrôlent les flux de Pods sélectionnés, selon ce que le CNI implémente. Par défaut, en l'absence de NetworkPolicy applicable, les Pods ne sont pas nécessairement isolés par une politique réseau Kubernetes. Une règle \`default deny\` sans autorisation complémentaire peut empêcher :

- l'accès des clients via le routeur;
- la résolution DNS;
- l'accès aux systèmes d'identité;
- la télémétrie ou les backends de données.

Le lab ci-dessous comporte une NetworkPolicy volontairement **bloquante** avec listes \`ingress: []\` et \`egress: []\`, pour un exercice de revue. Ce bundle n'est pas un déploiement fonctionnel.

### 5.1 Flux d'une API : inventorier avant d'autoriser

| Flux | Contrôle attendu | Risque |
|---|---|---|
| ingress → application | Source, ports et chemin compatibles avec ingress réel | Route présente mais backend inaccessible |
| application → DNS | Résolution interne via TCP/UDP selon besoin | Timeouts de toutes les dépendances |
| application → identity | Egress HTTPS à destination autorisée | Échec JWKS/OIDC |
| application → base | Port, authN, TLS, segment réseau | Refus métier ou exposition excessive |
| application → telemetry | Endpoint collector et droits | Perte de traces en incident |

Dans OCP, le trafic provenant de l'Ingress Controller peut dépendre du mode réseau, d'adresses source et de règles propres à la topologie. Ne jamais proposer une règle générique « autoriser le namespace ingress » comme universellement suffisante sans test sur le cluster cible.

## 6. Contrat offline : six ressources liées sans mutation de cluster

Le [bundle JSON du laboratoire](../../examples/v01/manifest-contract/02-deployment.json) contient :

1. Namespace pédagogique \`workshop-v01\`;
2. ServiceAccount \`ledger-reader\` sans montage automatique de token API;
3. Deployment à deux replicas, image volontairement impossible, securityContext restrictif;
4. Service ClusterIP avec targetPort nommé;
5. Route edge vers ce Service, hôte \`.invalid\`;
6. NetworkPolicy default-deny qui bloque le trafic de l'exemple.

**Ne pas exécuter \`oc apply\` sur ce bundle**. L'image n'existe pas et la NetworkPolicy interdit les flux. Le but est de tester la **cohérence structurelle** du contrat et d'étudier ce qu'il faudrait modifier, sous approbation, pour disposer d'un lab vivant dans un namespace isolé.

Le vérificateur offline lit les six fichiers JSON et contrôle les liens inter-ressources et certains invariants de sécurité. Il **ne remplace pas** la validation OpenAPI du serveur ni les contrôles SCC/PSA.

~~~bash
python -m examples.v01.manifest_contract
python -m unittest discover -s tests -p "test_*.py" -v
~~~

Le résultat \`PASS\` signifie seulement que l'exemple satisfait les règles **locales du livre**, pas qu'il sera admis par un cluster particulier.

## 7. Diagnostic : quel plan refuse le trafic ?

### 7.1 Déploiement refusé immédiatement

- Erreur \`Forbidden\` avec mention de permissions API : examiner identité et RBAC.
- Échec indiquant absence de SCC valide, profil PSA ou contrôle d'admission : examiner politique Pod et service account.
- Échec quota ou LimitRange : examiner les contraintes du namespace, pas le CNI.

### 7.2 Pod créé, mais non disponible

- \`Pending\` : scheduler, PVC, taints, requests.
- \`ImagePullBackOff\` : référence, registre, pull secret, DNS, CA.
- \`CrashLoopBackOff\` : application, UID, permissions, liveness, ressources.
- \`Running\` mais \`Ready=False\` : readiness, port, dépendances.

### 7.3 Route créée, mais erreur client

Les codes HTTP ne suffisent pas à identifier la cause : un même code peut être généré à plusieurs couches.

| Symptôme | Premières hypothèses à départager | Preuve |
|---|---|---|
| 403 | AuthN/AuthZ route ou application, policy externe | Logs corrélés, réponse et point d'émission |
| 503 | Aucun endpoint éligible, maintenance routeur, backend | EndpointSlices, route et logs du router |
| 502 | Réponse invalide ou échec de connexion backend | Router/app logs, TLS, ports |
| 504 | Timeout de proxy ou dépendance | Latence router/backend/traces |
| TLS handshake échoue | Certificat, SNI, mode TLS, CA | Connexion contrôlée, chaîne certifiée |

Ne pas ouvrir aveuglément NetworkPolicy, RBAC ou SCC pour faire disparaître l'erreur : rechercher d'abord **la frontière qui échoue**.

### 7.4 Commandes read-only

~~~bash
oc -n NAMESPACE get deploy,rs,pod,svc,route
oc -n NAMESPACE get endpointslices
oc -n NAMESPACE get networkpolicies
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc -n NAMESPACE describe pod NOM_POD
oc -n NAMESPACE describe route NOM_ROUTE
~~~

Selon permissions, certaines commandes peuvent retourner \`Forbidden\`. Ne pas élever ses droits simplement pour satisfaire un exercice.

## 8. Questions d'architecture à maîtriser

1. **Un « yes » de \`oc auth can-i\` suffit-il à créer un Pod ?** Non; admission peut refuser le Pod.
2. **SCC et PSA sont-ils interchangeables ?** Non; OpenShift utilise des mécanismes distincts.
3. **Faut-il changer la SCC par défaut pour une application privilégiée ?** Non; une SCC spécifique et approuvée est la démarche à examiner.
4. **Une Route edge chiffre-t-elle jusqu'au backend ?** Non, son modèle classique termine TLS au routeur; le flux interne doit être traité séparément.
5. **Un Service ClusterIP garantit-il des endpoints Ready ?** Non.
6. **Un default-deny NetworkPolicy peut-il bloquer la Route ?** Oui, suivant dataplane et sources réelles.
7. **Le lab JSON valide-t-il la conformité OCP ?** Non, seulement des règles locales de structure.
8. **Quelle est la première action d'un diagnostic N3 ?** Définir symptôme, périmètre, frontière et observations non destructives.

## Sources primaires

- [Red Hat — OCP 4.22 SCC](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/managing-pod-security-policies)
- [Red Hat — OCP 4.22 Pod Security Admission et interaction SCC](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/understanding-and-managing-pod-security-admission)
- [Red Hat — OCP 4.22 Routes et terminaison TLS](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/ingress_and_load_balancing/routes)
- [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes — Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

**Reste à prouver** : admission d'un manifest réel avec politique SCC/PSA effectivement observée, fonctionnement Route selon le CNI réel, validation du flux et logs. Aucune de ces validations runtime n'a été exécutée par ce chapitre.
