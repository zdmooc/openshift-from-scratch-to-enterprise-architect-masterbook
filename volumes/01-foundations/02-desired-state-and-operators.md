# 02 — Desired state, réconciliation et Operators

**Volume** : 01 · **Statut** : DRAFT · **Portée** : Kubernetes et OCP 4.22  
**Preuve principale** : PUBLIC_VERIFIED · **Vérifié** : 2026-10-11

## 1. Modèle déclaratif

Dans un système déclaratif, on exprime un objectif : par exemple, deux instances d'un service. Des contrôleurs observent les ressources et cherchent à faire converger la réalité vers cet objectif. On ne décrit pas toutes les actions impératives intermédiaires. Cette convergence peut être temporairement incomplète à cause de l'ordonnancement, d'erreurs d'image, du réseau ou d'un quota.

Notions à distinguer :
- **Spec** : intention désirée, généralement fournie par l'utilisateur ou un autre contrôleur.
- **Status** : état observé et signalé, éventuellement en retard sur le réel.
- **Reconciliation** : tentative idempotente de rapprocher état observé et état voulu.
- **Controller** : processus implémentant une boucle de contrôle.
- **Operator** : contrôleur spécialisé encapsulant des connaissances opérationnelles pour un logiciel ou un service.

## 2. Séquence de convergence conceptuelle

~~~mermaid
sequenceDiagram
  participant User as Platform Engineer
  participant API as Kubernetes API
  participant Ctrl as Controller
  participant K as Kubelet/Runtime
  User->>API: Applique la configuration désirée
  Ctrl->>API: Observe le nouveau state
  Ctrl->>API: Crée/ajuste les ressources nécessaires
  K->>API: Observe le Pod assigné
  K->>K: Tente l'exécution des containers
  K->>API: Publie les observations
  Ctrl->>API: Reconcile / met à jour status
~~~

Le diagramme simplifie plusieurs contrôleurs réels. Il ne signifie pas que le control plane exécute lui-même les containers applicatifs.

## 3. Pourquoi la réconciliation est critique en entreprise

- **Répétabilité** : le même contrat souhaité peut être évalué après un événement.
- **Résilience** : une panne ne nécessite pas toujours une intervention manuelle.
- **Observabilité** : conditions, events et metrics rendent visible la progression.
- **Gouvernance** : politique et droits encadrent qui peut changer l'intention.
- **Dangers** : une mauvaise intention déclarative peut être appliquée de manière très efficace; des garde-fous sont indispensables.

GitOps ajoute un autre niveau de convergence entre les manifests versionnés et l'état des ressources du cluster. **GitOps n'est pas identique au mécanisme interne de réconciliation Kubernetes.**

## 4. Cluster Operators, application Operators et OLM

Les Operators présents dans le fonctionnement même d'OpenShift peuvent gérer des composants de la plateforme. Les Operators dédiés aux applications automatisent leurs cycles de vie. Ne pas supposer qu'ils sont tous distribués, installés et mis à jour par un mécanisme unique : identifier explicitement leur modèle de gestion et les mécanismes adaptés à la version.

Pour concevoir un Operator de qualité :
- Définir un contrat de CRD stable et validable.
- Implémenter des reconcilers idempotents.
- Définir le sens des Conditions Ready/Progressing/Degraded.
- Tester les erreurs partielles et la récupération.
- Documenter RBAC et l'éventuelle leader election.
- Prévoir la suppression, la rétention des ressources et les migrations de version.

Le Volume 08 détaillera l'implémentation en Go et les alternatives.

## 5. Anti-patterns d'architecture

1. Lire seulement le nombre de replicas demandés sans vérifier les ready/available replicas.
2. Supposer que toutes les erreurs sont corrigées automatiquement, sans limite de retry.
3. Confondre idempotence théorique et tests d'idempotence.
4. Utiliser les droits administrateur pour masquer une politique RBAC insuffisante.
5. Appliquer des mutations de CRD à un cluster partagé sans plan de retour arrière.

## 6. Exercice de pensée

Un Pod reste Pending alors que son Deployment demande trois replicas. Formuler au moins quatre hypothèses indépendantes : ressources insuffisantes, contraintes de placement, quotas, PVC non disponible, topology spread, policy. Choisir les observations read-only avant toute action corrective.


## 7. Les événements, la cache et l'API : la boucle réelle

Un contrôleur Kubernetes ne se résume pas à un script qui exécute périodiquement `kubectl apply`. Les implémentations usuelles gèrent un flux de changements, mettent en file des clés d'objets et travaillent avec une vue mise en cache du cluster. Il faut raisonner sur l'**eventual consistency** : une écriture acceptée par l'API n'est pas nécessairement visible immédiatement dans toutes les caches de lecture.

~~~mermaid
flowchart LR
  API[API server] --> L[List initial]
  API --> W[Watch des changements]
  L --> CACHE[Cache d'objets]
  W --> CACHE
  CACHE --> Q[Workqueue de clés]
  Q --> R[Reconcile]
  R -->|lecture observée| CACHE
  R -->|mutations ciblées| API
  R -->|succès, requeue ou erreur| Q
~~~

Ce diagramme décrit un pattern courant de clients/contrôleurs, pas un mécanisme obligatoire pour tous les composants.

### 7.1 Quatre métadonnées à ne pas confondre

| Champ | À quoi il sert | Ce qu'il ne prouve pas |
|---|---|---|
| `metadata.uid` | Identité unique d'un objet pendant sa vie | Un nom identique ne garantit pas le même objet |
| `metadata.resourceVersion` | Version opaque pour concurrence et mécanismes list/watch | N'est pas un timestamp ni un compteur global ordonnable |
| `metadata.generation` | Révision de l'intention quand le serveur considère qu'une modification la déclenche | N'est pas le nombre de tentatives de reconcile |
| `status.conditions[].observedGeneration` (si présent) | Génération de l'intention évaluée par une condition | N'existe pas nécessairement pour tous les types/contrôleurs |

**Invariant utile** : une condition Ready=True avec un observedGeneration inférieur à metadata.generation doit être considérée comme potentiellement **périmée**. De même, un `status.observedGeneration` n'a un sens que si le type le définit et si le contrôleur le renseigne correctement.

### 7.2 List, Watch, déconnexion et ré-synchronisation

Le client charge un état par LIST puis suit les modifications avec WATCH à partir d'un `resourceVersion`. Cette valeur doit être traitée comme **opaque**. Elle n'est pas un compteur qu'un opérateur peut interpréter pour calculer une durée.

Un watch peut être interrompu ou faire référence à un historique expiré. Un code **410 Gone** indique typiquement qu'un `resourceVersion` trop ancien ne permet plus de reprendre ce flux : le client doit rétablir l'état par un nouveau LIST avant de WATCH à nouveau, selon les règles de la bibliothèque utilisée. Les bookmarks permettent certains marqueurs de progression mais ne sont pas garantis à intervalle fixe.

Pour des contrôleurs Go, préférer les primitives maintenues de **client-go** ou **controller-runtime** plutôt que de recréer sans nécessité les stratégies de watch/retry.

## 8. Contrat d'un Reconcile robuste

Le reconcile d'un service peut se décrire comme une fonction conceptuelle :

~~~text
reconcile(CR observée, ressources filles observées, contraintes externes)
    → opérations nécessaires + status + éventuelle requeue
~~~

Ce n'est pas une fonction mathématique pure : elle interagit avec un API server et parfois un système externe. L'enjeu est de rendre les **effets** idempotents et observables, même lorsque l'opération est relancée.

### 8.1 Algorithme recommandé (pseudocode)

~~~text
1. Charger la CR; si supprimée, ne rien faire.
2. Déterminer les défauts et valider le contrat (idéalement à l'admission).
3. Si deletionTimestamp présent : appliquer la politique de finalisation.
4. Calculer les ressources désirées depuis la spec.
5. Lire les ressources existantes et leurs propriétaires.
6. Corriger seulement les champs possédés par le contrôleur.
7. Observer les statuts des ressources filles.
8. Fixer Ready/Progressing/Degraded avec raison, message
   et observedGeneration quand le schéma le prévoit.
9. Retourner succès ou requeue/retry selon la nature de l'écart.
~~~

La boucle doit converger si elle est appelée deux, dix ou cent fois avec la même intention; elle doit aussi supporter un arrêt brutal **entre** deux opérations.

### 8.2 Succès de l'API ≠ ressource devenue Ready

Exemple : le contrôleur crée un Deployment. L'API accepte l'objet; aucun Pod n'est encore prêt. Le contrôleur doit distinguer :

- **Progressing=True** : des opérations utiles sont en cours.
- **Ready=False** : la condition de disponibilité n'est pas encore acquise.
- **Degraded=True** : un échec effectif empêche ou dégrade l'opération, selon le contrat de l'Operator.

Ces noms de conditions sont un **design de CRD**, non une obligation universelle de toutes les APIs Kubernetes. Il faut publier un contrat stable pour leur signification, sans marquer Degraded=True pour une attente normale de scheduling.

### 8.3 Classification des erreurs

| Erreur | Exemple | Conduite recommandée |
|---|---|---|
| Transitoire | API timeout, conflit d'écriture, dépendance temporaire | Retry borné/backoff, signal mesuré |
| Configuration | Référence inexistante, champ interdit | Condition explicite; éviter boucle agressive |
| Autorisation | RBAC interdit l'action requise | Degraded et remédiation gouvernée |
| Conflit de propriété | Champ déjà géré par un autre field manager | Ne pas forcer sans contrat de propriété |
| Dépendance fonctionnelle | Base temporairement non disponible | Adapter conditions/requeue sans réécrire sans cesse |
| Suppression | CR marquée deletionTimestamp | Finalisation bornée, politique de rétention |

**Avertissement** : si un contrôleur touche un système externe (base, file de messages, DNS), il faut gérer retries et idempotency keys propres au domaine. Une requête API Kubernetes répétable ne rend pas magiquement une transaction bancaire « exactly once ».

## 9. Field ownership et Server-Side Apply

Server-Side Apply (SSA) permet d'exprimer les champs qu'un gestionnaire souhaite contrôler. L'API conserve une information de propriété des champs dans `metadata.managedFields`. Un conflit peut se produire lorsqu'un autre gestionnaire détient un champ qu'on tente de modifier différemment.

Le principe est **d'attribuer une responsabilité** aux champs, pas de gagner tous les conflits en forçant.

### 9.1 Exemple conceptuel de partage de responsabilités

Un Operator possède `spec.template.spec.containers[name=api].image` d'un Deployment qu'il crée. Une équipe exploitation veut changer une annotation de monitoring, non l'image. Les deux modifications peuvent coexister si les champs sont correctement séparés. Si un autre contrôleur tente de devenir propriétaire de l'image avec une valeur différente, un conflit SSA doit conduire à une décision de gouvernance : quel composant est la source de vérité ?

**Ne pas** lancer `oc apply --server-side --force-conflicts` comme méthode générique de remédiation : le forçage transfère la propriété des champs et peut provoquer une guerre de réconciliation.

### 9.2 Inspecter sans muter

~~~bash
oc -n NAMESPACE get deployment NOM -o jsonpath='{.metadata.managedFields[*].manager}{"\n"}'
oc -n NAMESPACE get deployment NOM -o jsonpath='{.metadata.generation}{"\n"}{.status.observedGeneration}{"\n"}'
oc -n NAMESPACE describe deployment NOM
~~~

L'affichage de managedFields peut inclure plusieurs managers et ne constitue pas à lui seul une preuve qu'un conflit est actif. Les erreurs de mise à jour, Events et logs du contrôleur apportent le contexte.

## 10. Idempotence, convergence et invariants démontrables

L'Operator possède plusieurs propriétés distinctes :

- **Idempotence** : répéter le reconcile avec les mêmes conditions ne crée pas de nouveaux effets non souhaités.
- **Convergence** : après perturbation, le système rejoint finalement l'état désiré si les conditions nécessaires sont remplies.
- **Observabilité** : le statut et les métriques rendent intelligible le chemin vers l'état désiré.
- **Sûreté** : une restauration automatique n'efface pas de données ni n'étend arbitrairement des privilèges.
- **Liveness** : une condition corrigée permet au système de progresser, sans deadlock durable.

### 10.1 Cas de test nécessaires

| Scénario | Injection | Invariant |
|---|---|---|
| Premier reconcile | Ressource fille absente | Création une seule fois |
| Deuxième reconcile | Aucune modification | Pas de nouvelle écriture |
| Drift autorisé | Image changée manuellement | Retour à l'intention si l'Operator en est propriétaire |
| Drift non autorisé | Annotation gérée par un tiers | Ne pas l'effacer |
| Échec partiel | Deployment créé, Service échoue | Une reprise complète le Service sans dupliquer Deployment |
| Suppression contrôlée | CR marquée deletionTimestamp | Nettoyage/rétention suivant contrat |
| RBAC restreint | Écriture refusée | Condition explicite, pas d'élévation improvisée |
| Crash du leader | Replica actif indisponible | Reprise par nouveau leader sans duplication externe |

Pour une démonstration locale, un simulateur **offline** permet de prouver certains invariants algorithmiques sans OpenShift. Il ne valide pas CRI-O, l'API server ni les contraintes réelles de scheduling. Voir [L06 — simulateur de boucle](../../labs/06-controller-offline.md).

## 11. Le piège des deux boucles : GitOps et Operator

Deux contrôleurs peuvent toucher un même objet :

~~~mermaid
flowchart LR
  GIT[Git / source déclarative] --> ARGO[Argo CD]
  ARGO --> API[API Kubernetes]
  CR[Custom Resource] --> OP[Operator Go]
  OP --> API
  API --> CHILD[Deployment / Service]
~~~

L'architecture doit définir **qui possède chaque ressource et chaque champ**.

**Cas sain** : Argo CD possède la CR métier; l'Operator possède les Deployments et Services dérivés. L'Operator ne modifie pas les annotations métier de la CR que GitOps impose, sauf champs status.

**Cas conflictuel** : Argo CD et l'Operator possèdent simultanément le même Deployment et écrivent des images différentes. Chacun voit le changement de l'autre comme un drift. Le système peut rester en oscillation; une politique force=true aggrave souvent le phénomène.

Un arbitrage documentaire doit expliciter : source de vérité, API contractuelle, champ possédé, stratégie de rollback, ordre de suppression, sécurité RBAC et chemin d'escalade.

## 12. Leader election : disponibilité du contrôleur ≠ disponibilité du service

Pour un Operator répliqué, des instances peuvent concourir à un Lease Kubernetes, utilisé pour déterminer un leader actif. Cela réduit le risque de plusieurs reconcilers actifs sur les mêmes objets, **sans** constituer une garantie absolue pour des effets externes non transactionnels en cas de partition ou de transition.

Pour les opérations sensibles (facturation, publication d'un message, provisionnement externe) : idempotency key, jeton de fencing ou contrat métier équivalent peuvent être nécessaires. Les Leases ne sont pas à elles seules un protocole transactionnel distribué.

Inspection non destructive, si autorisée :

~~~bash
oc -n NAMESPACE get leases.coordination.k8s.io
oc -n NAMESPACE get deployment NOM_OPERATOR
oc -n NAMESPACE get pods -l app=NOM_OPERATOR
~~~

Les sélecteurs exacts sont à vérifier : `app=NOM_OPERATOR` est un exemple, pas un standard garanti.

## 13. Day-2 : scénarios de panne et récupération

### Cas A — Workload dérivé supprimé

Si la CR demeure et le controller continue de fonctionner, le reconcile peut recréer le Deployment. **Preuve attendue** : horodatage, UID de la ressource recréée, statut final, éventuelle interruption métier. Cette preuve n'existe pas simplement parce que le code contient un Get puis un Create.

### Cas B — CR invalide après upgrade

Une nouvelle version d'Operator exige un champ absent. L'architecture doit posséder une stratégie de versions de CRD, valeurs par défaut, conversion éventuelle et compatibilité arrière. Un schema validation rejetant la requête peut être préférable à un crash de la boucle.

### Cas C — RBAC perdu

Une modification GitOps retire le droit d'écriture sur les Deployments. Un Operator peut rester Running sans parvenir à réconcilier. Il doit rendre l'échec visible via logs, Conditions, métriques et Events, tout en évitant une boucle agressive qui surcharge l'API.

### Cas D — Une dépendance externe ne répond plus

Un Operator qui provisionne un système tiers doit distinguer : timeout avant exécution, exécution réussie mais réponse perdue, exécution refusée, ou résultat réellement inexistant. Réessayer aveuglément peut créer des doublons. Le contrat externe doit fournir une lecture idempotente ou un identifiant stable.

## 14. Grille de soutenance d'un Operator

| Question de comité | Exigence de réponse |
|---|---|
| Où est la source de vérité ? | CR/spec + responsabilité claire des ressources filles |
| Que devient une exécution interrompue après Create ? | Relecture, réconciliation et récupération idempotente |
| Comment sait-on que la dernière spec est prise en compte ? | Conditions et observedGeneration cohérents |
| Comment éviter le drift infini avec GitOps ? | Contrats de propriété d'objets/champs |
| Que fait le deuxième replica d'Operator ? | Participation à l'élection du leader ou répartition sûre |
| Comment se passe la suppression d'une CR ? | Retain/Delete, finalizer, orphelins et délais |
| Quelles preuves pour « operator production-ready » ? | Tests failure, sécurité, upgrade, observabilité, support et limites |

Les termes « Ready » et « Healthy » doivent toujours être rapprochés du contrat observable et d'un protocole de preuve.

## Références complémentaires

- [Kubernetes — Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Kubernetes — API Concepts / List-Watch](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Kubernetes — Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Kubernetes — Leases et leader election](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Red Hat — OCP 4.22 Operators](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview)

## Sources

- [Kubernetes — Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Red Hat — Operators overview 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview)
- [Red Hat — Control plane 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/control-plane)
