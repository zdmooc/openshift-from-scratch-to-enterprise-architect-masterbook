# 10 — N3 du control plane : observabilité, diagnostic, preuves et soutenance d'architecture

**Volume 02 · DRAFT · Cible OpenShift Container Platform 4.22**  
**Méthode : read-only par défaut, aucune intervention sur etcd, CVO, MCO ou kube-apiserver.**

## 1. Reconnaître le plan affecté

L'expression « le cluster est en panne » ne constitue pas un diagnostic. Un incident peut toucher :
- l'API, TLS, RBAC et admission;
- le control plane Kubernetes et etcd;
- CVO et un upgrade;
- MCO et les nœuds;
- scheduler et le placement;
- CRI-O/runtime et la création de containers;
- CSI/storage, OVN/DNS/Ingress;
- les applications métier et leurs dépendances externes.

Un runbook N3 commence par déterminer **qui voit l'erreur et quelle opération échoue**, pas par l'exécution d'un redémarrage.

## 2. Référence de triage minimal

~~~text
T0 : Client / utilisateur / automatisation a signalé ...
Heure locale + UTC : ...
Version OCP, Kubernetes, RHCOS : ...
Topologie : SNO / CRC / 3 masters / autre ...
Type d'échec : API / scheduling / runtime / image / storage / réseau / métier ...
Dernier changement connu : Git commit, release, MachineConfig ...
État observable : ClusterVersion, ClusterOperators, Nodes, MCP ...
Impact : succès métier, API, erreurs, périodes, périmètre ...
Données sensibles expurgées : oui/non ...
Hypothèses falsifiables : ...
~~~

Il faut préserver les conditions de collecte : une erreur Forbidden sur \`oc get\` relève d'un droit absent et ne doit pas être comptée comme l'absence d'un composant.

## 3. Commandes de base en lecture seule

~~~bash
oc version
oc get clusterversion -o yaml
oc get clusteroperators
oc get nodes -o wide
oc get machineconfigpools
oc -n openshift-etcd get pods
oc -n openshift-kube-apiserver get pods
oc -n openshift-kube-controller-manager get pods
oc -n openshift-kube-scheduler get pods
~~~

Certaines ressources sont sensibles et exigent des droits spécifiques. Le livre ne recommande pas de contourner RBAC ni d'utiliser un token cluster-admin pour un simple exercice.

### 3.1 Indices observables

| Signal | Signification immédiate | Question suivante |
|---|---|---|
| clusterversion Progressing | Convergence en cours | Quelle cible ? Depuis quand ? Quel composant attend ? |
| clusterversion Upgradeable=False | Blocage aux updates | Condition et raison exactes ? |
| etcd ClusterOperator Degraded | Santé ou convergence etcd dégradée | Quorum, nœud, certificat, latence ? |
| kube-apiserver Available=False | Exposition/serving API dégradé | TLS, backend, admission, etcd ? |
| machine-config Degraded | Nœud/pool non convergé | rendered config, drain, reboot ? |
| Pod Pending sans nodeName | Non placé | Events scheduler, ressources, taints ? |
| Pod OOMKilled | Container terminé sous pression mémoire | Limite, mémoire live, traces app ? |
| ImagePullBackOff | Image non disponible au runtime | Registre, auth, réseau, tag/digest ? |

Ce tableau sert à préparer une **expérience discriminante**, pas à prononcer une cause racine.

## 4. Métriques et logs du control plane

Principes SRE :
- mesurer le **taux d'erreur et la latence** de l'API par verbe/type de requête;
- observer les requêtes bloquées ou lentes, l'effet des webhooks;
- observer la santé etcd et sa latence disque;
- comparer scheduling attempts, queue/backlog et événements de nœud;
- surveiller CVO/ClusterOperators et durée d'upgrade;
- surveiller MCO/MCP et nombre de nœuds Updated/Degraded;
- corréler avec les SLI des services métiers.

La présence d'un dashboard n'est pas une preuve de son exhaustivité. Sur OpenShift, des composants de monitoring peuvent être gérés par Operators et avoir leurs propres domaines de panne.

### 4.1 Alertes qui méritent une action

- incapacité d'écrire de nouvelles ressources dans l'API;
- perte de quorum etcd ou santé membres critique;
- certificat proche d'expiration avec risque de rupture;
- ClusterOperator critique Degraded prolongé;
- rollout MCO qui empêche une maintenance;
- Pending Pods pour cause de manque réel de capacité;
- réussite métier inférieure au SLO malgré cluster apparemment sain.

Se demander : l'alerte a-t-elle un runbook, un propriétaire et une méthode claire d'arrêt d'escalade ?

## 5. Comment analyser un changement qui précède un incident

Une corrélation temporelle ne prouve pas que le changement est la cause, mais donne une hypothèse testable.

Pour un upgrade :
1. relever le commit / la cible de release;
2. contrôler la version affichée dans ClusterVersion;
3. identifier les ClusterOperators non Available ou Progressing;
4. relever les MCP et les nœuds concernés;
5. vérifier les effets sur API, DNS, Ingress, stockage et applications;
6. comparer aux mesures avant changement;
7. déterminer si l'incident précède le changement ou lui succède réellement.

Ne jamais « corriger » l'état apparent en forçant des Conditions ou en supprimant des ressources de plateforme pour qu'elles se recréent sans procédure supportée.

## 6. Tableau N3 : six cas

### A — oc get renvoie Forbidden

**Faits :** réponse 403 pour un namespace, autres opérations autorisées.  
**Hypothèses :** RBAC, sujet, namespace, ressource.  
**À exclure :** problème de quorum généralisé, parce que l'API traite la requête.  
**Action initiale :** tester can-i et vérifier les bindings, sans demander cluster-admin par défaut.

### B — Pod Pending après saturation mémoire

**Faits :** le scheduler indique Insufficient memory.  
**Hypothèses :** sum(requests) et allocatable saturés, overhead, quota.  
**À exclure :** nœud « libre » selon seul top CPU/RAM instantané.  
**Action :** bilan demandes/reservations, puis décision de capacité ou optimisation.

### C — CVO Progressing après update

**Faits :** release désirée différente de celle observée, un ClusterOperator Degraded.  
**Hypothèses :** blocage de dépendance, MCO, API, téléchargement d'image, certificat.  
**Action :** collecter ClusterVersion, cause précise du ClusterOperator, MCP, version de release. Un downgrade n'est pas une commande de secours.

### D — etcd Degraded et API lente

**Faits :** latences API élevées, ClusterOperator etcd Degraded.  
**Hypothèses :** I/O, quorum, réseau entre membres, certificats, instabilité du leader.  
**Action :** préserver les nœuds sains, identifier les événements, suivre la procédure de support; aucun restore improvisé.

### E — Webhook d'admission indisponible

**Faits :** créations de Pods refusées par un webhook; Pods existants continuent de servir.  
**Hypothèses :** service webhook indisponible, certificat CA, timeout, rules scope.  
**Action :** identifier le service et la politique failurePolicy, puis une résolution supportée par son propriétaire. Ne pas supprimer aveuglément les hooks sécurité.

### F — Après un rollout MCO un worker ne revient pas Ready

**Faits :** MCP partiellement Updated, node NotReady/Degraded.  
**Hypothèses :** drain, reboot, service OS, registry, rendu config.  
**Action :** identifier le nœud et la rendered MachineConfig concernés, comparer Events/Conditions avant toute mutation.

## 7. Dossier de preuve et audit

Le même incident peut être décrit à trois niveaux :

| Niveau | Contenu |
|---|---|
| **Observation** | Commande, date, contexte et sortie expurgée |
| **Interprétation** | Hypothèse et degré de confiance |
| **Conclusion** | Cause établie par preuve/expérience ou non confirmée |

Une sortie de \`oc get nodes\` peut contenir des noms/IP internes. Les sorties de Secrets et les dumps etcd sont très sensibles. Écarter toute pièce pouvant exposer données clients, tokens, accès SSH ou clés privées du dépôt public.

### 7.1 Incident à impact bancaire

Une plateforme de paiements peut afficher tous les Pods Ready et rencontrer malgré tout des échecs de transaction en raison d'un broker, d'une DB, d'un IdP, d'un token, d'un moteur de décision ou d'un circuit réseau externe.

Le N3 cluster doit travailler avec la corrélation transactionnelle et éviter les conclusions de cause « OpenShift » uniquement parce que l'application y est hébergée.

## 8. Modèle de revue d'architecture pour le control plane

| Domaine | Exigence | Méthode de preuve |
|---|---|---|
| API | Disponibilité pour lecture et écriture | Tests représentatifs et métriques API |
| etcd | Quorum et stockage performants | Monitoring, test panne autorisé |
| Maintenance | MCO/drain n'interrompt pas un service au-delà du contrat | Drills et PDB/capacité |
| Updates | Chemin supporté, releases signées, rollback/résolution documentés | Préflight et compte rendu |
| Identité | Certificats, RBAC et admission résilients | Tests négatifs et rotation |
| Security | SCC/PSA et webhooks cohérents | Admission test et audit |
| API extensions | CRD versionnées, conversion disponible | Tests upgrades sur CRs existantes |
| SRE | Alerts et SLO mesurables | Dashboard, incident replay |
| Continuité | RPO/RTO réellement mesurés | Restore end-to-end, indépendant |

Le tableau est un **contrat à valider**, pas un résultat « PASS » présumé.

## 9. Évaluation d'architecte

1. Pourquoi un Pod Pending n'est-il pas un problème de runtime CRI-O ?
2. Comment distinguer RBAC et SCC ?
3. Que prouve etcd Degraded et que ne prouve-t-il pas ?
4. Pourquoi une release CVO Healthy ne suffit-elle pas à un SLO bancaire ?
5. Quelle différence entre MachineConfigPool et MachineConfiguration ?
6. Quel risque systémique apporte un webhook en failurePolicy=Fail ?
7. Pourquoi les certificats/API LB font-ils partie de la HA du control plane ?
8. Comment prouver la fraîcheur d'une Condition sur une CRD ?
9. Pourquoi un snapshot etcd ne couvre-t-il pas les données d'application ?
10. Comment éviter d'exposer des secrets dans un rapport N3 ?

### Critère pédagogique suggéré

Réussite si les dix réponses distinguent causalité, responsabilité et preuve. Il ne s'agit pas d'une certification produit ni d'un jugement de capacité professionnelle.

## 10. Limites de l'édition

Le lecteur doit traiter les exemples comme des **méthodes** et non des procédures d'intervention autorisées en production. Les modifications aux composants etcd, CVO, MCO, admission et plan de contrôle nécessitent des runbooks officiels et une gouvernance de changement stricte.

## Sources

- [Red Hat — OCP 4.22 Architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — Updating clusters](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/understanding-openshift-updates-1)
- [Red Hat — Machine configuration](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_configuration/machine-config-index)
- [Red Hat — Cluster Operators](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operators/operator-reference)
- [Red Hat — Backup/restore control plane](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/backup_and_restore/control-plane-backup-and-restore)

**Aucun test runtime sur CRC** et aucune preuve HA/PRA nouvelle dans cette édition.


## 11. Diagnostic à plusieurs hypothèses : ne pas confondre corrélation et causalité

Une panne d'application après upgrade et un etcd Operator Degraded ne suffisent pas à attribuer l'incident à etcd. Trois événements peuvent coïncider sans causalité directe. Le N3 doit construire un **graphe d'hypothèses** et rechercher des signaux qui départagent.

Exemple fictif : après déploiement, 25 % des appels de consultation bancaire dépassent leur timeout.

Hypothèses :
- H1 : readiness insuffisamment stricte, Service sélectionne un backend non fonctionnel;
- H2 : réduction du CPU limit et throttling d'application;
- H3 : saturation de la base externe;
- H4 : changement de certificats/identité causant des retries;
- H5 : lenteur de l'API Kubernetes ayant retardé le rollout, sans causer les timeouts des transactions déjà routées.

Chaque hypothèse demande **une preuve discriminante**. H1 : état des endpoints + logs de readiness; H2 : métriques de throttling et comparaison de releases; H3 : DB pool, requêtes et p99 SQL; H4 : erreurs TLS/validation; H5 : chronologie rollout et latence control plane, puis relation avec les appels HTTP existants.

### 11.1 Table factuelle minimale

| Observation | Ce que cela prouve | Ce que cela ne prouve pas |
|---|---|---|
| API kube-apiserver répond /readyz | Health local selon endpoint | Service métier disponible |
| etcd majorité possible | Topologie théoriquement suffisante | Leader stable et latence acceptable |
| Pod Running | Processus existant | Requête correctement autorisée |
| Deployment Available | Critères de disponibilité du contrôleur | SLO banque |
| GitOps Synced | Révision déclarée reconciliée | Intégrité de données externes |
| PVC Bound | Claim liée à un volume | Restore testé |
| CVO Available | Signal opérateur de version | Compatibilité complète des add-ons |

## 12. Un incident N3 doit être reproductible

Le runbook doit contenir :
1. version OCP, composants et IDs non sensibles;
2. intervalle de temps en UTC et fuseau de collecte;
3. commandes read-only et droits utilisés;
4. sorties expurgées et source de chaque métrique;
5. hypothèses supportées/refutées;
6. comparatif avec le dernier état sain;
7. décision et acteur habilité;
8. contrôle post-correction par SLI;
9. risque résiduel et suivi d'actions.

Des logs pris **après** un redémarrage peuvent avoir perdu la séquence critique. Lorsque c'est permis, préserver les observations avant toute mutation.

## 13. Revue d'une plateforme de paiement : gates avant production

| Gate | Question | Preuve nécessaire |
|---|---|---|
| API | Existe-t-il un chemin redondant jusqu'à kube-apiserver ? | Test LB/DNS/certificats |
| Quorum | Des domaines de panne indépendants protègent-ils etcd ? | Topologie et panne contrôlée |
| MCO | Mise à jour des nœuds sans indisponibilité excessive ? | Preflight PDB + drill |
| OLM/CRDs | Versions compatibles, conversion sûre ? | Tests objets existants |
| Sécurité | SCC, PSA et webhooks refusent les mauvaises configs ? | Tests d'admission négatifs |
| Exécution | kubelet/CRI-O savent démarrer l'image cible ? | Test sandbox par digest |
| Storage | Snapshot/backup/restore cohérents ? | Contrôle d'intégrité |
| SRE | SLO métier instrumentés, alertes actionnables ? | Baseline et incident replay |
| Green IT | Requests/limits et énergie justifiées ? | Sizing, mesures, hypothèses |
| Changement | Rollback appli ou stratégie recovery cluster explicites ? | ADR, runbook approuvé |

Aucun résultat PASS ne découle de l'existence de ce tableau. Chacun doit recevoir une preuve et une date.

## 14. Séquence de récupération : ne pas « réparer » le mauvais plan

Un N3 intervient souvent sous pression. La première décision de sécurité est **de ne pas ajouter un incident**.

- Si un Pod est Pending, regarder scheduler et volumes, pas redémarrer etcd.
- Si l'API retourne 403, examiner identity/RBAC, pas manipuler le load balancer.
- Si un webhook bloque une création, vérifier service/TLS/selector et sa politique; ne pas désactiver tous les webhooks.
- Si CVO progresse vers une nouvelle release, relever les Conditions et l'historique avant toute décision.
- Si MCO Degraded, ne pas effacer la rendered MachineConfig sans procédure supportée.
- Si etcd perd le quorum, ne pas essayer un restore improvisé sur un cluster de production ni sur CRC.
- Si le service bancaire échoue avec Pods Ready, rechercher dépendances et règles métier.

La remédiation doit toujours être associée au **contrôle de retour à la normale**, avec preuve de transaction si elle concerne un service métier.

## 15. Exercices corrigés

**E1 : Pod Running mais aucun endpoint Ready.** Vérifier labels, selector Service, readiness et EndpointSlices. Running n'assure pas l'éligibilité au routage.

**E2 : 403 à la création d'un Pod.** Distinguer refus RBAC de rejet admission; inspecter la réponse exacte et le service account de workload. Les privileges humains ne suffisent pas à autoriser une SCC pour tous les Pods.

**E3 : PDB bloque un drain.** Calculer replicas disponibles et autorisation d'éviction, puis évaluer la capacité restante. Ne pas supprimer le PDB par réflexe.

**E4 : trois masters mais panne de quorum sur perte d'un rack.** Deux membres partagent le même rack. Réviser la cartographie de domaines de panne : trois membres ne garantissent pas trois domaines indépendants.

**E5 : certificat API invalide mais etcd sain.** Un client peut être bloqué au handshake TLS avant authentification; corriger la chaîne de confiance, pas étendre RBAC.

**E6 : un PV Bound ne remonte plus après panne de zone.** Regarder topology, CSI et volumes physiques; Kubernetes n'invente pas de réplique du volume. RPO/RTO nécessitent backup/restore validés.

## Références complémentaires

- [Kubernetes — Debugging Kubernetes nodes](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
- [Kubernetes — Service](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Red Hat OpenShift 4.22 — Monitoring](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/monitoring/index)
