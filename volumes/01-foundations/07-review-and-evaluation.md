# 07 — Évaluation technique et soutenance d'architecture du Volume 01

**Statut : DRAFT · PUBLIC_VERIFIED pour les concepts / PAPER_LAB pour les cas**  
Ce chapitre propose des réponses modèles et non une certification professionnelle.

## A. Questions de compréhension

| Question | Réponse attendue |
|---|---|
| 1. Conteneur vs VM ? | Le conteneur partage ordinairement le noyau hôte; la VM a son noyau invité |
| 2. Namespace vs cgroup ? | Isolement d'une vue d'objets vs contrôle d'utilisation de ressources |
| 3. Le root du conteneur peut-il être dangereux ? | Oui, selon user namespaces, privilèges, montages, capabilities et sockets exposées |
| 4. OCI image vs OCI runtime ? | Format de l'artefact vs modèle d'exécution d'un bundle |
| 5. Tag vs digest ? | Nom mutable selon la politique vs identifiant cryptographique du contenu |
| 6. Digest = signature ? | Non, ne prouve pas l'identité ni le processus de publication |
| 7. CRI-O vs kubelet ? | Runtime gérant l'exécution via CRI vs agent de nœud chargé des Pods assignés |
| 8. Deployment vs Pod ? | Contrôleur de réplicas/rollouts vs unité d'exécution |
| 9. Que stocke etcd ? | État persistant de l'API du cluster, sans en faire une base applicative |
| 10. Scheduler vs kubelet ? | Choix du nœud vs mise en œuvre locale de l'état du Pod |
| 11. Request vs limit CPU ? | Besoin de planification/part relative vs plafond de consommation |
| 12. Request mémoire vs limit mémoire ? | Besoin de planification vs plafond de mémoire |
| 13. Running vs Ready ? | État de cycle de vie vs disponibilité déclarée selon critères de readiness |
| 14. Un Service crée-t-il des Pods ? | Non; il sélectionne des backends, il ne déploie pas l'application |
| 15. À quoi sert EndpointSlice ? | Modéliser les endpoints d'un Service |
| 16. Une Route corrige-t-elle un endpoint absent ? | Non, elle fournit une exposition, pas une application fonctionnelle |
| 17. Une SCC est-elle un RBAC Role ? | Non; rôle d'autorisation API vs contraintes d'admission Pod |
| 18. CVO vs OLM ? | Gestion de la version/Cluster Operators vs gestion de certains Operators add-on |
| 19. CRC valide-t-il la HA multi-nœud ? | Non, pas s'il n'y a qu'un seul domaine de panne |
| 20. Un PodDisruptionBudget protège-t-il de toutes les pannes ? | Non; il concerne des évictions volontaires et a des limites |
| 21. Un CronJob offre-t-il exactement-once ? | Non; concevoir idempotence et gestion des réessais |
| 22. Pourquoi ne pas confondre GitOps Synced et transaction OK ? | Sync reflète l'état de gestion déclarative, non la réussite métier |
| 23. Un scan SBOM valide-t-il l'absence de vulnérabilités ? | Non; dépend de couverture, base de vulnérabilités, instant du contrôle |
| 24. Pourquoi choisir un UID arbitraire ? | Adaptation aux politiques de sécurité et réduction d'hypothèses privilégiées |
| 25. Quel est le début d'un diagnostic N3 ? | Symptomatique, périmètre et hypothèses observables avant mutations |

## B. Scénarios à résoudre

### Scénario 1 — Pod Pending après un déploiement

Trois Pods sont demandés. Deux sont Running, le troisième Pending. Le nœud affiche 35 % CPU utilisé.

**Attendu** : ne pas déduire de l'usage CPU que le placement est possible. Examiner les Events, requests, allocatable, taints/tolerations, volumes, affinités, quotas et limites de nombre de Pods. Vérifier si le troisième Pod a déjà un nodeName.

### Scénario 2 — Image non-root incapable d'écrire

L'application échoue sur l'écriture de /var/log/app alors qu'elle démarrait localement avec Docker.

**Attendu** : identifier UID effectif et contraintes SCC, vérifier le propriétaire et le mode du chemin, les montages et SELinux. Proposer une sortie structurée stdout/stderr ou un volume approprié plutôt qu'un contournement privileged/chmod global.

### Scénario 3 — Service sans backend

Le Deployment annonce deux Pods Ready mais aucune réponse sur un Service.

**Attendu** : comparer le sélecteur Service avec les labels Pod; vérifier EndpointSlices, ports, listener, NetworkPolicies, DNS et traces réseau, et différencier chemin routage vs identité applicative.

### Scénario 4 — Cluster sain, métier indisponible

La console OpenShift ne signale pas de ClusterOperator dégradé; pourtant 20 % des paiements échouent.

**Attendu** : distinguer plateforme vs application; vérifier SLI métier, base externe, files MQ, erreurs d'authentification, timeouts, tracing, corrélation et taux de retries. L'état global du cluster ne suffit pas.

### Scénario 5 — Comité d'architecture exige un PRA

Le seul test existe sur CRC mono-nœud, et le projet annonce un RTO de 15 minutes sans drill.

**Attendu** : refuser de qualifier RTO/HA prouvés; documenter le caractère INFERRED, proposer test DR sur topologie représentative, sauvegarde, restauration, intégrité et dépendances externes. RTO 15 min est ici un **objectif hypothétique**, non une performance démontrée.

## C. Barème de revue

| Axe | 0 | 1 | 2 |
|---|---|---|---|
| Exactitude mécanismes | Confusions | Vocabulaire partiel | Explication causale correcte |
| Diagnostic | Mutations au hasard | Hypothèses faibles | Hypothèses → observations → exclusion |
| Sécurité | Privilèges excessifs | Mesures partielles | Contrôles proportionnés et testés |
| Disponibilité | Promesse non prouvée | Scénario incomplet | Domaine de panne et protocole de test |
| Traçabilité | Pas de version | Références partielles | Version, sources, statut de preuve |
| Architecture | Choix arbitraires | Arguments généraux | Choix/NFR/compromis explicites |

**Réussite pédagogique suggérée** : au moins 9/12, sans note 0 en sécurité ni traçabilité. Ce seuil est une proposition éditoriale, non une certification.

## D. Travaux pratiques reliés

- [L01 — Observation de cluster](../../labs/01-cluster-read-only.md)
- [L02 — Linux namespaces/cgroups](../../labs/02-linux-cgroup-readonly.md)
- [L03 — Inspection OCI](../../labs/03-oci-image-readonly.md)
- [L04 — API et triage](../../labs/04-kubernetes-api-triage-readonly.md)
- [L05 — Revue architecture bancaire](../../labs/05-architecture-review-payments.md)

## E. Ce que le Volume 01 ne prouve pas encore

- Aucun test d'échec multinœud.
- Aucun chiffrage de performance validé.
- Aucune conformité réglementaire démontrée.
- Aucun benchmark runtime effectué pendant cette rédaction.
- Aucun test de compatibilité ou de security scan des exemples d'image.

La revue technique et la validation des labs sont nécessaires avant de déclarer le Volume 01 **FINAL**.
