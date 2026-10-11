# 13 — Fiabilité, ressources, SLI/SLO et capacité de service sur OpenShift

**Volume 01 — édition 1.0 · Statut : DRAFT avant QA · Niveau : SRE / Architecte Solutions**  
**Concepts Kubernetes et OpenShift 4.22 ; dimensionnements pédagogiques marqués INFERRED.**

## 1. Pourquoi le statut d'un Pod ne constitue pas un SLO

Une plateforme peut être saine alors qu'un paiement n'est pas traité. À l'inverse, des ressources plateforme peuvent être dégradées sans impact visible immédiat sur un service. Le SRE doit décider **quels résultats sont importants pour l'utilisateur** et bâtir une chaîne d'observation qui relie l'expérience métier aux dépendances techniques.

Trois indicateurs fondamentaux :
- **Disponibilité** : proportion des demandes éligibles donnant un résultat conforme sur une période.
- **Latence** : distribution de temps de réponse d'une opération fonctionnelle identifiable.
- **Correction fonctionnelle** : exactitude/complétude de données et traitements, mesurée par une vérification indépendante.

Les signaux CPU, mémoire, Pods Ready, PVC, queues et logs sont nécessaires au diagnostic, mais sont rarement eux-mêmes les SLI métier.

## 2. SLI, SLO, SLA et error budget

- **SLI** (Service Level Indicator) : mesure avec numérateur, dénominateur et exclusions.
- **SLO** (Service Level Objective) : objectif choisi pour ce SLI sur une période.
- **SLA** (Service Level Agreement) : engagement contractuel susceptible de prévoir des conséquences.
- **Error budget** : tolérance à la dégradation compatible avec l'objectif choisi.

### Exemple numérique, entièrement fictif

Supposons un objectif SLO de 99,9 % de demandes éligibles réussies pendant 30 jours et un trafic constant de 10 000 demandes éligibles par jour.

~~~text
Demandes éligibles = 30 × 10 000 = 300 000
Fraction d'échec maximale = 1 - 0,999 = 0,001
Budget = 300 000 × 0,001 = 300 demandes en erreur
~~~

Si le trafic n'est pas constant, une traduction du pourcentage en **minutes d'indisponibilité** est approximative. Si les requêtes sont rares, un budget fondé uniquement sur le taux de requêtes peut cacher une période d'indisponibilité prolongée. Un SLO de disponibilité temporelle et un SLO de succès par requête ne sont pas des instruments identiques.

### 2.1 Définir précisément le dénominateur

Pour une API de paiement, les erreurs métier attendues (par exemple une demande non autorisée correctement rejetée) ne doivent pas nécessairement être comptées comme pannes techniques. Toutefois, exclure de façon opportuniste les requêtes complexes rend le SLO trompeur. Les règles doivent être fixées **avant** les incidents et approuvées avec le propriétaire métier.

## 3. Requests, limits et limites de l'observation instantanée

Un nœud peut afficher 15 % de CPU moyen et refuser un Pod à 100m si les requests des Pods déjà placés ont épuisé sa capacité allocatable, ou si le nouveau Pod ne tolère pas un taint, ne peut pas monter son PV ou atteint un quota.

Formellement, pour la ressource CPU seule :

~~~text
Σ(request CPU des Pods prévus) <= CPU allocatable du nœud
~~~

C'est une condition nécessaire pour ce critère dans le modèle de scheduling standard, **pas une condition suffisante pour le placement**.

### 3.1 CPU limit et throttling

Si le container dispose d'une limite CPU plus basse que ses pics, le noyau peut faire du throttling. L'usage CPU moyen agrégé peut sembler raisonnable alors que le p99 de latence est élevé. Chercher les métriques de throttling par container, la consommation au pas de temps adapté et l'évolution du latency histogram.

### 3.2 Mémoire et OOM

La mémoire ne se throttlera pas de manière analogue au CPU. Sous pression d'une limite mémoire, des allocations peuvent échouer ou provoquer des terminaisons OOM. L'événement \`OOMKilled\` doit être mis en regard de la limite **du conteneur**, de la mémoire live, du cache, des pics et du comportement GC. L'augmentation de limite peut traiter un pic légitime ou masquer une fuite : décider sur mesures.

## 4. Probes et contrats de santé

| Probe | Signal | Ne prouve pas |
|---|---|---|
| startupProbe | L'application a terminé une phase de démarrage spécifique | Que les dépendances seront toujours disponibles |
| readinessProbe | Le Pod peut recevoir le trafic selon un contrat local | SLO métier complet |
| livenessProbe | Le processus doit-il être redémarré ? | La disponibilité globale d'un partenaire externe |

Éviter de relier une livenessProbe à une base externe : une coupure de base peut provoquer le redémarrage en boucle de tous les Pods, aggravant l'incident. Un circuit-breaker ou une degradation de readiness peut être plus approprié selon la fonction.

### 4.1 Grâce de terminaison et rollout

Lors d'une mise à jour, il faut tenir compte du délai d'arrêt, des requêtes en vol, des connexions persistantes et de la réplication. La période \`terminationGracePeriodSeconds\` donne un cadre au kubelet avant une terminaison forcée. Le Pod doit gérer SIGTERM. Un Deployment Available à la fin du rollout n'est pas une preuve de zéro erreur en transition.

## 5. PodDisruptionBudget et topologie des pannes

Un PDB borne certaines évictions **volontaires** et ne protège pas contre la perte brutale d'un nœud. Une distribution \`topologySpreadConstraints\` ou une anti-affinité préférentielle peut réduire la concentration de Pods selon la topologie disponible; l'effet réel doit être observé.

Sur CRC à un seul nœud, aucune valeur de PDB ou anti-affinité ne crée de second domaine de panne. Pour démontrer une panne de nœud tolérée, exiger une topologie multinœud et les mesures de temps de rétablissement.

## 6. HPA et saisonnalité

Un HPA ajuste les replicas à partir de métriques définies, sous réserve du système de métriques et des politiques applicables. Le HPA ne crée pas de nœuds ; l'autoscaling de la capacité machine est un autre mécanisme, disponible et configuré selon la plateforme.

Questions de conception :
- quel est le signal d'échelle : CPU moyen, requêtes/s, queue depth, métrique métier ?
- quelle est la latence entre le pic et la disponibilité de nouveaux Pods ?
- les limites de base/messaging suivent-elles l'échelle ?
- que faire lorsque le cluster n'a plus de capacité ?
- comment plafonner les coûts et empêcher un retry storm ?
- quels scénarios sont trop rapides pour un HPA réactif ?

### Exemple numérique

Un Pod traite **fictivement** 75 requêtes/s à une latence cible et une consommation mesurée de 500m CPU. Pour 900 requêtes/s, la première approximation est 900/75 = **12 Pods**. Mais ce quotient suppose une réponse quasi linéaire et une absence d'effet partagé. La décision doit intégrer la mémoire, les p95/p99, les DB pools, les quotas et la tolérance à une zone indisponible.

Si chaque Pod demande 500m et 512 Mi, les 12 Pods demandent **6 CPU et 6 Gi** au niveau applicatif, sans overhead ni réserve de DR. La planification doit ajouter le coût des nouveaux Pods durant une mise à jour \`maxSurge\`.

## 7. Alerting : lien de causalité et actionnabilité

Une alerte opérationnelle doit être :
- **actionnable** : une équipe peut intervenir de manière définie;
- **contextualisée** : propriétaire, priorité, runbook, liens;
- **mesurée** : pas uniquement un état de Pod isolé;
- **stable** : fenêtre et règles évitant le bruit.

Métriques exemples :
- ratio d'erreurs métiers, succès API, latence et volumes de requêtes;
- restarts, Pod Ready, rollout stalled, requests vs allocatable;
- throttling CPU, mémoire proche de limite, pressure;
- queue age/depth, taux retries et échecs des dépendances.

Une erreur budgétaire supérieure au taux toléré sur plusieurs fenêtres constitue un signal plus utile qu'un seuil arbitraire CPU > 70 % pour une API critique. La règle doit être évaluée sur des données réelles.

## 8. Dimensionner pour le mode dégradé

Un design avec trois zones et trois pools de capacité doit être évalué **après perte de la plus grande zone**. Une plateforme qui gère la charge nominale ne possède pas automatiquement assez de marge pour accueillir les Pods évincés.

Construire le calcul :
1. demandes en charge nominale, par environnement;
2. demandes plateforme, DaemonSets, sidecars et sécurité;
3. capacité allocatable par nœud et réserves de rollout;
4. répartition de Pods par zone/worker;
5. capacité survivante après le scénario de panne;
6. pic prévu pendant la panne;
7. seuil d'échelle et disponibilité des dépendances.

**Erreur classique :** multiplier les replicas par trois, mais placer les données dans un volume non montable hors d'une zone.

## 9. Performance et empreinte environnementale

La réduction carbone exige une chaîne de mesure et des frontières méthodologiques. Relever :
- transactions par heure et CPU-seconde par transaction;
- GiB-heure de mémoire demandée et consommée;
- réseau/stockage par transaction;
- énergie instrumentée (W ou kWh), si disponible;
- facteur d'émission régional et période, versionné;
- taux de surprovisionnement et opportunités de consolidation.

Ne pas inventer une consommation énergétique à partir d'un pourcentage CPU : la relation dépend du serveur, des composants, de la charge, de la mesure au mur et des conditions d'exploitation. **FinOps et Green IT peuvent être en tension avec le HA**, car les réserves de sécurité consomment des ressources; les arbitrages doivent être visibles.

## 10. Exercices d'architecture

**Cas A : CPU faible et latence élevée.** Rechercher throttling, I/O, DB, pool, DNS, locks et saturation des dépendances, pas seulement dimensionner davantage de Pods.

**Cas B : HPA monte à 30 replicas mais erreurs augmentent.** Vérifier que la base ou le broker supporte cette concurrence; rechercher tempête de connexions et limites réseau.

**Cas C : PDB empêche un drain.** Analyser minAvailable/maxUnavailable et placement réel; un PDB ne doit pas être désactivé automatiquement pour débloquer une maintenance.

**Cas D : quatre replicas sur CRC mono-nœud.** La disponibilité face à la panne de ce nœud reste nulle; proposer une topologie et des tests adaptés à une réelle HA.

## 11. Contrat de preuve

Pour qualifier une configuration de **RUNTIME_PROVEN**, enregistrer le commit, la version OCP, la topologie, le protocole de charge, les observations horodatées, les valeurs de métriques et les limites. Une capture \`oc top nodes\` ne constitue pas un benchmark de transaction.

## Sources

- [Kubernetes — Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Kubernetes — Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Kubernetes — Pod Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Kubernetes — HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Red Hat OCP 4.22 — Monitoring](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/monitoring/index)
