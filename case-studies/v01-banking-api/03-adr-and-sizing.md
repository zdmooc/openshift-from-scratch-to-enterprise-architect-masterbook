# V01-C03 — ADR et pré-dimensionnement justifiés d'une API bancaire

**Statut : REFERENCE_ARCHITECTURE / INFERRED · Aucune mesure réelle · Hypothèses explicitement fictives**

## 1. Contrat non fonctionnel à instruire

Une proposition d'architecture doit transformer une intention du métier en un **système de mesures** :

| Exigence | Exemple d'indicateur | Validation nécessaire |
|---|---|---|
| Disponibilité | Succès des requêtes éligibles | Mesure bout en bout sur période |
| Latence | p95/p99 des lectures statut | Charge représentative et dépendances |
| Intégrité | Absence de réponse incohérente pour identifiant donné | Cas fonctionnels et référentiel d'oracle |
| Confidentialité | Refus d'accès hors périmètre | Tests négatifs identités et objets |
| Résilience | Rétablissement après panne de domaine | Test représentatif de panne |
| Auditabilité | Chaîne commit/digest/approbation | Contrôle de la traçabilité |
| Sobriété | CPU-seconde et octets par transaction | Mesures instrumentées; données énergétiques traçables |

Ne pas promettre un RTO ou un SLO simplement parce que le cluster possède plusieurs replicas.

## 2. Exemple chiffré : construire une hypothèse de capacité

On suppose **fictivement** :

- charge de pointe : 600 requêtes/s ;
- consommation CPU moyenne de l'API mesurée dans un test synthétique : 12 millisecondes CPU par requête ;
- cible de taux d'utilisation CPU de 60 % pendant la pointe pour laisser une marge ;
- request CPU par Pod : 500m ;
- mémoire observée par Pod : 300 Mi ; request mémoire envisagé : 384 Mi ;
- aucune dépense CPU des proxys, agents, composants plateforme ou dépendances n'est incluse.

Calcul initial du besoin CPU :

~~~text
600 requêtes/s × 0,012 CPU-s/requête = 7,2 CPU de service
7,2 CPU / 0,60 = 12 CPU de capacité utile visée
12 CPU / 0,5 CPU-request par Pod = 24 Pods demandés
24 Pods × 384 Mi = 9 216 Mi = 9 Gi de requests mémoire
~~~

Ce dimensionnement est **une hypothèse mécanique**, pas une recommandation de prod :

- La moyenne CPU ne prédit pas le p99, la contention ni les pauses GC.
- Les backends externes peuvent saturer bien avant les Pods.
- Les limites CPU peuvent imposer du throttling.
- Le nombre de Pods dépend aussi du maximum par nœud et de la topologie.
- Un target 60 % ne compense pas automatiquement la panne d'un nœud.
- Le nombre de replicas obtenu doit être testé, pas simplement arrondi et approuvé.

### 2.1 Capacité en mode dégradé

Supposons 3 zones portant chacune 8 Pods (fictif). La perte d'une zone laisse 16 Pods à 500m requests, soit **8 CPU demandés**, inférieurs à l'objectif de 12 CPU utiles à la pointe. Même si les 16 Pods restants supportent une charge supérieure à leur request, rien ne valide ici le service à la pointe. Il faudrait revoir la répartition, les réserves, les seuils d'autoscaling et mesurer le scénario.

Un argument de HA doit donner les **ressources survivantes après perte**, le temps de replacement et les performances mesurées en mode dégradé, pas seulement le nombre de zones.

### 2.2 Contraintes de ressources

Le dimensionnement doit ensuite ajouter : DaemonSets et overhead, composants de plateforme, sidecars, réserve d'upgrade et drain, buffers de file, mémoire de processus, volumétrie des logs, stockage et bande passante. Une demande de 24 Pods sur un mono-nœud ne signifie pas qu'ils peuvent être déployés si quota, CPU, mémoire et limites de Pods ne le permettent pas.

## 3. ADR-001 — Modèle d'hébergement

**Contexte** : héberger une API réglementée avec contrôle d'identité, intégration interne et gouvernance de versions.

**Options** : OpenShift autogéré, OpenShift managé, Kubernetes managé, VM classique.

**Critères** : compatibilité workloads, contrôles de sécurité, intégrations réseau, SLO support, responsabilités, coût complet, compétence d'exploitation, trajectoire d'évolution.

**Décision** : **OUVERTE**. Aucun environnement cible n'a été sélectionné dans cette étude.

**Conséquence** : produire une comparaison pondérée et une matrice partagée des responsabilités avant investissement.

## 4. ADR-002 — Isolation et multi-environnements

**Contexte** : plusieurs équipes et environnements, partage du cluster envisagé.

**Options** : isolation par namespaces; clusters distincts par environnement; combinaison des deux.

**Décision de référence** : isoler les workloads par projet, avec RBAC, quotas, network policies et contrats de service accounts; exiger une analyse de risque pour déterminer si la production doit résider sur une frontière de cluster distincte.

**Risques** : cluster-admin partagés, blast radius d'un upgrade, quotas globaux, dépendances monitoring/réseau communes.

**Preuve attendue** : tests RBAC négatifs et flux refusés, démonstration de quotas et revue du plan de gestion des changements.

## 5. ADR-003 — Exposition de l'API

**Contexte** : API HTTPS pour clients autorisés, base interne non exposée.

**Décision de référence** : entrée au travers d'un point d'ingress gouverné vers un Service interne. Terminaison TLS et ré-encryptage ou passthrough à décider selon exigences, gestion de clés et architecture réseau.

**Risques** : certificats, mauvais routage, erreurs d'autorisation, headers non fiables, dépendance LB/DNS.

**Preuve** : connectivité depuis les réseaux prévus, refus hors périmètre, politiques de certificat, probes et SLI fonctionnel.

## 6. ADR-004 — Données et événements

**Contexte** : statuts de paiement persistants, audit et intégration événementielle.

**Décision de référence** : stockage transactionnel géré séparément du Pod stateless, publication événementielle avec contrat de duplication et de reprise explicite. Pas de persistance des données critiques dans la couche éphémère du conteneur.

**Risques** : SPOF du référentiel, indisponibilité du broker, messages dupliqués, délais de réplication, backups incohérents.

**Preuve** : test restore, audit de schémas et contrats d'événements, tests d'idempotence.

## 7. ADR-005 — GitOps et séparation des propriétés

**Contexte** : les manifestes sont livrés via GitOps et une partie de la plateforme peut être créée par Operator.

**Décision de référence** : déclarer la CR dans Git si un Operator est responsable des ressources filles; ne pas écrire les mêmes fields simultanément depuis Argo CD et un Operator.

**Risques** : oscillation de réconciliation, contournement RBAC, rollbacks destructifs, dérive manuelle.

**Preuve** : revue managedFields, tests de drift/self-heal et absence de changements non autorisés.

## 8. ADR-006 — Santé et continuité

**Contexte** : le service doit survivre à des pannes documentées.

**Décision de référence** : probes alignées sur comportement réel, réplication et placement fondés sur domaines de panne, dépendances surveillées, runbooks, restauration de données testée.

**Limites** : aucune preuve de HA multinœud ou de PRA sur CRC mono-nœud.

## 9. Matrice de preuve et prochaine action

| Risque | Test minimal | Où ? | Statut |
|---|---|---|---|
| Crash d'un Pod | Interrompre une réplique et contrôler SLI | Sandbox autorisé | NON TESTÉ |
| Perte d'un nœud | Panne contrôlée et mesure d'impact | Environnement multinœud | NON TESTÉ |
| Mauvaise image | Admission/politique refuse l'artefact | Cluster de test | NON TESTÉ |
| Token invalide | Requête refusée sans divulgation | Environnement app de test | NON TESTÉ |
| Egress interdit | Refus réseau vérifié sans élargir policy | Environnement de test | NON TESTÉ |
| Broker indisponible | Stratégie de retry/ack contrôlée | Environnement d'intégration | NON TESTÉ |
| Backup/restore | Restauration et intégrité contrôlées | Environnement de reprise | NON TESTÉ |

**Critère de publication du dossier d'architecture** : retirer le statut INFERRED de chaque exigence **uniquement** quand la preuve spécifique existe. Aucune ligne ne doit être maquillée en RUNTIME_PROVEN.

## Sources

- [Kubernetes — scheduling](https://kubernetes.io/docs/concepts/scheduling-eviction/)
- [Kubernetes — resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [OpenShift 4.22 — architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
