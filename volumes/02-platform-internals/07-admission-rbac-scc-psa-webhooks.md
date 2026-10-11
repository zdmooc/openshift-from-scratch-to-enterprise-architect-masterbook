# 07 — Admission interne : RBAC, SCC, PSA, webhooks et quotas

**Volume 02 · DRAFT · Référence OCP 4.22.**  
**Ce chapitre distingue contrôles API, sécurité de l'exécution et politique métier.**

## 1. La demande API traverse plusieurs décisions

Quand un Pod est créé, le résultat dépend de son auteur, du service account, de ses caractéristiques et des contrôles actifs. L'admission n'est pas une simple vérification finale : certains plugins peuvent **ajouter des valeurs** et d'autres **refuser** un objet.

~~~mermaid
flowchart TD
 A[Requête HTTPS] --> B[Authentification]
 B --> C[Autorisation]
 C --> D[Admission mutante]
 D --> E[Admission validante]
 E --> F[Persistance API]
 F --> G[Reconcile / kubelet]
~~~

Ce schéma est pédagogique. Les contrôleurs d'admission ont un ordre documenté mais l'organisation interne peut être plus complexe que ce pipeline simplifié. Le principe demeure : être autorisé à soumettre une requête ne prouve pas qu'elle est admissible.

## 2. Droits d'auteur de la demande et identité de Pod

Il faut différencier :
- l'utilisateur humain ou pipeline qui crée le Deployment;
- le controller qui crée ultérieurement le ReplicaSet/Pod;
- le service account désigné dans le PodSpec;
- les autorisations de ce service account pour appeler l'API après démarrage;
- les droits d'accès métier de l'application à ses données.

Red Hat OCP 4.22 précise que, pour les ressources de workload comme Deployment, la sélection de SCC à l'admission du Pod s'appuie sur le **service account du Pod**. Il est donc insuffisant d'affirmer qu'un administrateur humain peut utiliser une SCC pour en déduire que tous les Pods du Deployment peuvent la consommer.

## 3. SCC : sélection, defaulting puis validation

Une **Security Context Constraint** autorise ou interdit des paramètres comme l'UID, les groupes de fichiers, les capacités Linux, le mode privileged, hostNetwork et hostPath. Elle peut aussi générer des valeurs par défaut (notamment un UID à partir d'une plage de namespace) avant de valider.

Par exemple, le SCC restricted-v2 utilise une stratégie MustRunAsRange pour runAsUser et se réfère à l'annotation de namespace définissant la plage autorisée. Mettre arbitrairement runAsUser: 1000 peut donc échouer si 1000 est hors plage du projet.

### Modèle de sûreté des images

Une image bien adaptée :
1. ne requiert pas root;
2. tolère un UID de processus non déterminé pendant le build;
3. a des chemins exécutables lisibles par l'UID assigné;
4. écrit les données temporaires dans des emplacements prévus;
5. n'exige pas de hostPath, hostPID ou privilèges génériques;
6. utilise une politique de capabilities minimale.

À l'inverse, ajouter privileged=true pour résoudre Permission denied élargit la surface d'attaque sans démontrer la cause.

### Diagnostic des SCC affectées

Une fois le Pod admis, une annotation telle que openshift.io/scc peut révéler la SCC utilisée, si l'objet et les permissions de lecture permettent de la voir. L'absence de Pod en cas de rejet rend cette approche impossible : consulter alors les messages d'admission sur le controller propriétaire et les Events.

Exemples read-only :

~~~bash
oc -n NAMESPACE get pod POD -o jsonpath='{.metadata.annotations.openshift\.io/scc}{"\n"}'
oc -n NAMESPACE describe deployment DEPLOYMENT
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc get scc
~~~

Les commandes doivent suivre les permissions autorisées. Ne pas partager les logs contenant des secrets ou détails sensibles.

## 4. Pod Security Admission et Pod Security Standards

Kubernetes définit des niveaux PSS :
- privileged : le moins restrictif;
- baseline : empêche des escalades connues;
- restricted : modèle de durcissement plus fort.

PSA applique ces profils en modes :
- **enforce** : peut rejeter le Pod non conforme;
- **warn** : produit un avertissement;
- **audit** : enregistre un signal d'audit.

Red Hat documente, pour OCP 4.22, que SCC et PSA sont **deux mécanismes indépendants**. La SCC peut muter des valeurs, valider ensuite la spec, puis PSA valide selon le profil du namespace. Il faut satisfaire les deux, sans déduire l'un de l'autre.

### 4.1 Synchronisation des labels warn/audit

OpenShift possède un mécanisme de synchronisation des labels PSA warn/audit en fonction des permissions SCC des ServiceAccounts présents dans le namespace. Cette logique vise à réduire des avertissements incohérents lorsque des comptes sont habilités à des SCC particulières.

**Point subtil :** les privilèges personnels de l'utilisateur lançant un Pod directement ne sont pas nécessairement inclus dans cette synchronisation. En production, la bonne méthode est de définir les service accounts et privilèges effectifs du workload, pas de se fonder sur un label PSA aperçu isolément.

## 5. Webhooks : extensibilité et domaine de panne

Kubernetes prend en charge des webhooks d'admission qui peuvent valider ou muter des requêtes. Ces webhooks créent une dépendance opérationnelle de l'API vers un service additionnel.

Risques à étudier :
- service de webhook indisponible ou sans endpoint;
- certificat TLS/CA expiré ou incorrect;
- latence excessive et timeouts;
- failurePolicy inadapté au risque;
- règles matchant trop de types d'objets;
- règle empêchant sa propre réparation (bootstrap deadlock);
- mutation conflictuelle avec le gestionnaire GitOps ou l'Operator.

Un webhook configuré avec failurePolicy=Fail peut entraîner un rejet en cas d'échec de l'appel. Avec Ignore, certaines erreurs de webhook peuvent ne pas empêcher la requête; c'est un arbitrage de sécurité, pas une option à inverser automatiquement.

### 5.1 Revue obligatoire d'un webhook critique

| Axe | Question |
|---|---|
| Disponibilité | Le service possède-t-il la topologie adéquate ? |
| Certificats | Qui émet et renouvelle la CA et les certificats ? |
| Timeout | Le délai est-il mesuré et borné ? |
| Bootstrap | Le webhook peut-il être reconstruit quand il est indisponible ? |
| Scope | Exclut-il les namespaces composants essentiels quand nécessaire ? |
| Audit | Sait-on pourquoi une requête a été refusée ? |
| Réversibilité | Existe-t-il une procédure supportée en cas de panne ? |

## 6. Quota, LimitRange et ResourceQuota

La création peut être refusée à cause d'un ResourceQuota ou d'un LimitRange. Un request CPU absent peut recevoir une valeur implicite selon les policies; il faut inspecter le résultat admis et les messages de rejet.

Le quota n'est pas un contrôleur de capacité physique. Il empêche un namespace de déclarer/consommer certaines catégories de ressources au-delà d'un budget; il ne crée pas de machines ni ne garantit que le scheduler trouvera un nœud.

## 7. Chaîne d'investigation d'un Pod rejeté

1. **L'objet Deployment existe-t-il ?** Sinon analyser l'erreur d'API (RBAC/validation).
2. **Le ReplicaSet est-il créé ?** Examiner les conditions et Events du Deployment.
3. **Un Pod a-t-il été créé ?** Sinon les Events ReplicaSet peuvent contenir le refus d'admission.
4. **Une SCC est-elle applicable au service account ?** Examiner les grants autorisés.
5. **Le profil PSA est-il compatible ?** Examiner labels et règles du namespace, sans conclure depuis un seul label.
6. **Un webhook a-t-il rejeté la requête ?** Lire la raison et la dépendance, éviter le contournement général.
7. **Le Pod existe et Pending ?** Passer au scheduler et au stockage; ce n'est plus nécessairement un incident d'admission.

## 8. Exemple de Pod de référence non déployable

~~~yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-training
  namespace: training-only
spec:
  automountServiceAccountToken: false
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: api
    image: registry.example.invalid/app@sha256:REPLACE_WITH_REAL_DIGEST
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop: ["ALL"]
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 512Mi
~~~

La forme du manifest est pédagogique; l'image/digest n'existe pas. Son admission dépendra aussi des policies réelles du cluster; **ne pas appliquer** sur un namespace partagé.

## 9. Questions d'architecte

1. Pourquoi RBAC yes ne garantit-il pas qu'un Pod démarre ?
2. Pourquoi la SCC du service account est-elle essentielle pour un Deployment ?
3. Quelles valeurs une SCC peut-elle apporter au PodSpec ?
4. En quoi PSA est-il indépendant de SCC ?
5. Pourquoi un webhook d'admission constitue-t-il une dépendance du control plane ?
6. Dans quel cas failurePolicy=Fail peut-il accroître l'indisponibilité ?
7. Quelle différence entre rejet quota et FailedScheduling ?
8. Comment limiter les exceptions privileged ?

## Sources

- [Red Hat OCP 4.22 — Managing SCC](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/managing-pod-security-policies)
- [Red Hat OCP 4.22 — PSA and SCC interactions](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/understanding-and-managing-pod-security-admission)
- [Kubernetes — Dynamic Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/)
- [Kubernetes — RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes — ResourceQuotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

**Limites :** conception et diagnostic documentaires; aucune admission SCC/PSA exécutée sur le CRC durant cette itération.


## 10. De la requête Deployment à l'admission du Pod

Le contrôleur de Deployment n'exécute pas les conteneurs. Il demande au ReplicaSet de créer des Pods portant un service account spécifique. L'admission du Pod évalue les droits SCC du sujet concerné et du ServiceAccount selon les règles OpenShift. Les droits du développeur humain ne peuvent pas être transposés sans vérification au compte technique employé par l'application.

### 10.1 Exigences de sécurité minimales

| Propriété | But de sécurité | Condition de succès |
|---|---|---|
| runAsNonRoot | Éviter le processus root | Image compatible UID réellement assigné |
| seccomp RuntimeDefault | Filtrer certains appels système | Profil disponible et compatible |
| allowPrivilegeEscalation=false | Éviter élévations | Binaires et fonctionnalités compatibles |
| drop ALL capabilities | Limiter les privilèges Linux | Ajouter exceptions minimales si requises |
| readOnlyRootFilesystem | Réduire modifications persistantes de l'image | Chemins temporaires/volumes adaptés |
| automountServiceAccountToken=false | Réduire exposition de credentials API | L'app ne dépend pas de l'API Kubernetes |

Ces options ne remplacent ni l'autorisation métier OIDC ni NetworkPolicy. Elles doivent être testées avec les SCC réellement disponibles.

### 10.2 SCC requise : capacité et risque

OCP 4.22 documente l'annotation openshift.io/required-scc sur un Pod template pour demander explicitement une SCC autorisée. Elle peut permettre de stabiliser une exigence de sécurité lorsque plusieurs SCC seraient applicables, mais elle provoque un échec d'admission si la SCC n'est pas disponible ou pas autorisée pour le workload.

Il faut appliquer l'annotation au **template du contrôleur**, non modifier un Pod déjà en exécution pour contourner un refus. La gestion des droits du verbe use sur une SCC reste un acte d'administration de sécurité.

## 11. Limiter le blast radius des webhooks

Un webhook dynamique peut empêcher la création d'objets de l'API. Il ne s'agit pas seulement d'une bibliothèque appelée par les applications : c'est une dépendance de disponibilité du control plane.

### Scénario d'incident

Une politique de sécurité est exposée par un Service de webhook dont les Pods sont tous non Ready. Le webhook possède failurePolicy=Fail et des règles de sélection trop larges. Certains nouveaux Deployments ne peuvent plus créer de Pods, alors que les Pods déjà démarrés fonctionnent.

Questions diagnostiques :
1. Quel webhook exact a rejeté ou ralenti la demande ?
2. Son service Kubernetes possède-t-il des endpoints prêts ?
3. Le certificat du webhook correspond-il à son service et à sa CA ?
4. Le timeout est-il observé sur les appels concernés ?
5. Les namespaceSelectors et objectSelectors excluent-ils les composants critiques si prévu ?
6. Sa propre infrastructure dépend-elle de ressources qu'il pourrait refuser ?
7. Quelle procédure approuvée permet de rétablir la policy sans ouvrir toutes les permissions ?

**Ne pas** modifier failurePolicy en Ignore comme correctif universel : cela peut autoriser les objets que le contrôle était chargé de rejeter.

## 12. Revue d'admission à partir d'un objet non déployable

~~~yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-api
  namespace: example-workshop
spec:
  replicas: 2
  selector:
    matchLabels: {app: sample-api}
  template:
    metadata:
      labels: {app: sample-api}
    spec:
      serviceAccountName: sample-api
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        seccompProfile: {type: RuntimeDefault}
      containers:
      - name: api
        image: registry.example.invalid/sample@sha256:REPLACE_ME
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
        resources:
          requests: {cpu: 100m, memory: 128Mi}
          limits: {cpu: 500m, memory: 512Mi}
~~~

Ce Deployment est explicitement **non déployable** : image fictive, service account et namespace non créés, endpoint applicatif non fourni. Le rôle de l'exercice est de faire une revue de schema et de sécurité sur papier.

Questions :
- Pourquoi les permissions de créer le Deployment ne prouvent-elles pas la capacité à créer le Pod ?
- Quelle SCC est utilisable par le service account du template ?
- Le namespace impose-t-il un profil PSA restrictif ?
- Un webhook mutateur peut-il toucher des champs possédés par GitOps ?
- La valeur d'UID de l'image est-elle compatible avec la SCC ?

## 13. Registre d'exceptions de sécurité

Une demande de SCC custom ou privilégiée doit être documentée :

| Champ | Preuve requise |
|---|---|
| Besoin | Fonction ne pouvant pas être obtenue en non-root |
| Périmètre | Service account et namespace concernés |
| Permissions | Capabilities et volumes précis requis |
| Alternatives | Solutions sans privilèges étudiées et écartées |
| Sécurité | Risques d'hôte, réseau et identité |
| Durée | Date de revue et stratégie de retrait de l'exception |
| Tests | Admission positive et tentative négative non autorisée |

L'objectif n'est pas de rendre tous les Pods identiques : c'est d'obtenir le niveau de privilège minimal explicable et vérifiable pour chaque responsabilité.

## Sources d'approfondissement

- [Red Hat OCP 4.22 — SCC, required-scc et droits use](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/managing-pod-security-policies)
- [Kubernetes — Admission webhook best practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/)
