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
