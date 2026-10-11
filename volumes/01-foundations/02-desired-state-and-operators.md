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

## Sources

- [Kubernetes — Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Red Hat — Operators overview 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operators-overview)
- [Red Hat — Control plane 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/control-plane)
