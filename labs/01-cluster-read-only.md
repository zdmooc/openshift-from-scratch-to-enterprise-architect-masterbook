# Lab OCP-RO-01 — Première observation d'un cluster OpenShift

**Statut** : PROCEDURE_DOCUMENTED_NOT_EXECUTED · **Mode** : READ_ONLY  
**Durée** : selon contexte · **Cluster** : CRC ou autre OCP avec accès autorisé

## Objectif

Identifier les versions et l'état apparent du cluster sans générer de nouvelles charges. Observer n'est pas valider la résilience, le support ou l'état complet de production.

## Préflight

- oc disponible dans le terminal et contexte configuré.
- Droits de lecture adaptés.
- Ne pas exécuter depuis un environnement contenant des jetons ou secrets à capturer.
- Ne pas publier d'informations permettant l'identification de personnes ou systèmes non publics.

## Commandes

~~~bash
# Contrôle client et contexte
oc version
oc config current-context

# Métadonnées du cluster
oc get clusterversion
oc get nodes -o wide
oc get clusteroperators

# Inventaire logique (si droits suffisants)
oc get projects
oc get deployment -A
oc get statefulsets -A

# Pression / consommation si métriques disponibles
oc adm top nodes
~~~

Ces commandes réalisent des lectures API; **oc config current-context** peut révéler un nom local ou une cible interne. Ne publier aucune sortie brute sans revue.

## Résultats attendus

- Une version de cluster lisible (si autorisée).
- Un état des nœuds et des ClusterOperators, y compris dégradations éventuelles.
- Un inventaire de workloads limités aux namespaces accessibles.
- Des métriques de consommation uniquement si le service métriques et RBAC le permettent.

Une erreur RBAC ou un service métriques indisponible doit être consignés comme limitation, pas corrigés par élévation de privilèges improvisée.

## Grille de preuve

| Champ | À relever |
|---|---|
| Horodatage | Date et fuseau |
| Contexte | Lab / préproduction / production, anonymisé |
| OCP Version | Valeur de clusterversion |
| Visibilité | Permissions effectives de lecture |
| Santé | Nœuds, Operators; ne conclure que sur les points observés |
| Limites | Métriques ou namespaces absents |
| Protection | Absence de secret et anonymisation vérifiées |

## Cleanup

Aucune ressource créée : rien à supprimer.

**Attention** : ce lab n'a pas été exécuté au cours de l'initialisation du Masterbook.
