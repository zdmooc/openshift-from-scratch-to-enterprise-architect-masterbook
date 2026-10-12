# 09 — Control plane HA : domaines de panne, etcd, DNS, LB et certificats

**Volume 02 · ÉDITION 1.2 — RELECTURE DOCUMENTAIRE · Architecture de référence OCP 4.22**  
**Objectif : mesurer ce que signifie réellement survivre à une panne de contrôle.**

## 1. Pourquoi compter les masters ne suffit pas

Un cluster comportant trois nœuds control plane peut être correctement dimensionné ou exposé à un point unique de panne. Leur présence dans l'inventaire ne prouve pas :
- une séparation réelle de racks, zones, alimentations ou hyperviseurs;
- un load balancer sain pour l'API;
- la possibilité d'obtenir un quorum etcd après panne;
- des disques et un réseau suffisamment performants;
- des certificats non expirés;
- un backup/restauration opérationnel;
- la disponibilité des dépendances externes.

La haute disponibilité est une propriété **de la chaîne entière**, pas d'un seul composant.

## 2. Modèle de dépendances

~~~mermaid
flowchart TD
  CLIENT[oc / contrôleurs externes] --> DNS[DNS API endpoint]
  DNS --> LB[Load balancer API]
  LB --> A1[kube-apiserver A]
  LB --> A2[kube-apiserver B]
  LB --> A3[kube-apiserver C]
  A1 --> ETCD[Quorum etcd]
  A2 --> ETCD
  A3 --> ETCD
  ETCD --> DISK[Disques et réseau inter-membres]
  A1 --> CERT[Certificats et trust]
  A2 --> CERT
  A3 --> CERT
  SCH[Scheduler/controller-manager] --> LB
  K[kubelets] --> LB
~~~

C'est un schéma logique, pas une assertion que tous les composants accèdent exclusivement via ce LB ou que leurs flux exacts sont identiques. Les chemins internes du control plane et des static Pods dépendent de l'architecture OCP.

### 2.1 Quorum etcd et domaines de panne

Un ensemble de trois membres etcd tolère une perte de membre en conservant une majorité de deux, toutes choses égales par ailleurs. Mais si deux membres sont hébergés sur un même domaine électrique, la perte de ce domaine peut entraîner une perte de quorum. Une répartition logique sur trois nœuds ne suffit pas à garantir trois domaines physiques indépendants.

La tolérance d'une panne de nœud doit être testée sur une topologie représentative, pas inférée depuis un CRC mono-nœud.

## 3. La disponibilité API a plusieurs dimensions

Distinguer :
- **accessibilité réseau** de l'adresse API;
- **TLS correct** et chaîne de confiance;
- **identité et droits** du demandeur;
- **capacité de lecture** du kube-apiserver;
- **capacité d'écriture persistante** vers etcd;
- **convergence** des contrôleurs et des agents après écriture;
- **performance** sous la charge réelle.

Une réponse 401/403 peut coexister avec une API saine. Un HTTP 200 de health check ne prouve pas la capacité de réconcilier des ressources applicatives ni la disponibilité du service métier.

## 4. DNS, load balancer et certificats

Le point d'entrée de l'API doit rester accessible même si une instance devient indisponible. Les sondes de health du LB doivent vérifier la propriété appropriée et éviter de maintenir des instances réellement non aptes à traiter la requête.

Les certificats protègent l'identité du serveur et les connexions; leur rotation peut être automatisée par la plateforme, mais la disponibilité d'une CA, des tokens et des connexions existantes demeure une responsabilité de la gouvernance.

### 4.1 Symptômes TLS

| Symptôme | Première hypothèse | Exclusion nécessaire |
|---|---|---|
| Certificat non approuvé | CA/trust store erronés | Ne pas accepter insecure par défaut |
| SAN ne correspond pas au host | Nom DNS/LB ou certificat incohérent | Vérifier le nom réellement demandé |
| Certificat expiré | Cycle de renouvellement défaillant | Examiner le composant qui l'émet |
| Connexion refusée avant TLS | LB/firewall/route | Une correction de CA n'aidera pas |
| 401/403 après TLS | Identité/RBAC/admission | Le handshake s'est déjà déroulé |

**Anti-pattern dangereux** : proposer \`--insecure-skip-tls-verify\` comme correction d'architecture. Cela supprime une vérification d'identité essentielle et peut masquer une mauvaise configuration ou une interception.

## 5. Certificats et dépendances de l'upgrade

Les mises à jour OpenShift peuvent affecter plusieurs composants gérés : kube-apiserver, Operators, nœuds, API services et certificats. Les ressources et comportements évoluent selon release et channel.

Avant une mise à jour :
- vérifier Available/Progressing/Degraded/Upgradeable;
- vérifier la chaîne d'approvisionnement et la release image;
- revoir les incompatibilités des Operators additionnels et API versions;
- confirmer les backups compatibles etcd;
- vérifier la rotation des certificats et les dépendances TLS;
- établir capacité de drain par pool;
- prévoir mesures SLI avant, pendant et après.

Red Hat ne supporte pas un downgrade ordinaire du cluster vers une version antérieure pour annuler une mise à jour. Un plan de retour arrière doit donc être fondé sur **la procédure supportée**, pas sur un simple rollback Git.

## 6. Tableau de scénarios de défaillance

| Incident | Impact possible | Test représentatif |
|---|---|---|
| Un control-plane node indisponible | Quorum 2/3 préservé sous conditions | Nœud isolé, API/etcd/latence surveillées |
| Deux membres etcd indisponibles | Quorum perdu | Exercice dédié et supporté, pas sur CRC |
| Load balancer API indisponible | Impossible de joindre API externe | Test de redondance LB |
| Certificat API expiré | Clients rejettent TLS | Test gestion et renouvellement |
| DNS API inaccessible | Clients ne localisent plus l'endpoint | Tests depuis plusieurs réseaux |
| Latence disque etcd élevée | API lente, opérations bloquées | Profil I/O et métriques inter-membres |
| Webhook admission indisponible | Refus ou délai de création | Injection en sandbox avec protocole rollback |
| MCP Degraded pendant upgrade | Rollout nœuds incomplet | Drill sur cluster de test |

Toutes les lignes ci-dessus sont des **hypothèses d'essai**, pas des tests exécutés. Un test de panne contrôlée peut être dangereux pour les données et doit s'effectuer uniquement avec autorisation, sauvegarde et plan de reprise.

## 7. Control plane et disponibilité des workloads déjà déployés

La perte partielle ou totale de l'API n'arrête pas nécessairement tous les processus applicatifs déjà en cours d'exécution. Toutefois, elle perturbe la capacité à gérer les ressources, programmer de nouveaux Pods, répondre à certains changements et récupérer de certaines pannes.

Il est donc possible qu'un client métier accède encore à l'API applicative pendant qu'un administrateur ne peut plus créer de Deployment. **Cela ne signifie pas que la plateforme est résiliente** : une panne supplémentaire ou une échéance de certificat peut révéler le risque accumulé.

## 8. Hosted control planes : frontière d'hébergement différente

OpenShift 4.22 documente les hosted control planes, qui séparent davantage l'hébergement du plan de contrôle et celui des workers. C'est une autre décision d'architecture : l'API et les composants de contrôle peuvent résider sur une plateforme de management plutôt que sur les machines de calcul du cluster hébergé.

Ce modèle peut modifier les responsabilités de réseau, certificats, déploiement, disaster recovery et blast radius. Il ne suffit pas de déplacer des Pods de contrôle pour obtenir des garanties HA universelles; les contraintes de support, la topologie et les procédures de reprise spécifiques doivent être étudiées.

## 9. Méthode de preuve : RTO/RPO

Pour toute affirmation « API résiliente à la perte d'un nœud », produire :
- date, version OCP et architecture physique/logique;
- composants et domaines effectivement indépendants;
- état initial des ClusterOperators et d'etcd;
- protocole exact de panne;
- SLI de l'API, temps de réponse et disponibilité d'écriture;
- effet sur scheduling/controllers et applications;
- mesures temporelles jusqu'au rétablissement;
- résultat, écart par rapport à l'objectif et limites.

La valeur RTO n'existe pas parce qu'un diagramme affiche trois nœuds. Elle se **mesure** après un scénario représentatif. Le RPO d'etcd et celui d'une base métier sont deux engagements séparés.

## 10. Inspection non destructive

~~~bash
oc get nodes -o wide
oc get clusterversion
oc get clusteroperators
oc -n openshift-etcd get pods
oc -n openshift-kube-apiserver get pods
oc get machineconfigpools
~~~

Ces lectures nécessitent des droits et n'offrent pas à elles seules un test de quorum. Le livre ne fournit pas de script pour isoler/détruire des membres etcd sur des clusters partagés.

## 11. Questions d'architecture

1. Pourquoi « trois masters » est-il une preuve insuffisante de HA ?
2. Quel impact d'une panne DNS API sans panne des kube-apiservers ?
3. Comment un certificat expiré peut-il imiter une indisponibilité d'API ?
4. Qu'apporte une séparation de domaines de panne à etcd ?
5. Une API indisponible arrête-t-elle nécessairement les workloads en cours ?
6. Pourquoi le downgrade cluster n'est-il pas le plan standard de retour arrière ?
7. En quoi un hosted control plane change-t-il le domaine de responsabilité ?
8. Comment mesurer RTO et RPO plutôt que les déclarer ?

## Sources

- [Red Hat — Architecture OpenShift 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — Hosted control planes 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/hosted_control_planes/hcp-overview)
- [Red Hat — Backup and restore](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/backup_and_restore/control-plane-backup-and-restore)
- [Red Hat — Updating clusters 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/updating_clusters/understanding-openshift-updates-1)

**Statut :** architecture/documentation, sans test de panne réelle.


## 12. Quantifier une tolérance à la panne : analyse de domaines corrélés

Le calcul de quorum est une propriété mathématique des membres votants. L'architecture physique peut annuler cette tolérance apparente si plusieurs membres partagent un même domaine de panne.

Exemple de trois membres etcd :

| Membre | Zone | Rack | Alimentation |
|---|---|---|---|
| A | z1 | r1 | p1 |
| B | z2 | r2 | p2 |
| C | z3 | r3 | p3 |

Dans cette architecture fictive, perdre une zone retire un seul membre. Sous hypothèse de connectivité et stockage sains, une majorité reste possible. Mais si B et C utilisent réellement un storage-array unique, la perte du stockage peut retirer **deux membres** et détruire la majorité.

Pour chaque domaine à tester, dresser une matrice binaire composant × domaine de panne. Calculer les membres survivants et vérifier **toutes** les dépendances : etcd, API endpoint, LB, DNS, PKI, storage et réseau.

### 12.1 Un load balancer unique annule-t-il la HA ?

Un trio de kube-apiservers peut être sain, mais inaccessible depuis les clients si le VIP ou le load balancer de l'API est un SPOF. Le système peut continuer certaines opérations internes, mais les administrateurs et automates de déploiement ne peuvent plus interagir normalement.

Le dossier d'architecture doit préciser :
- nombre d'instances et répartition LB;
- stratégie de health checks et retrait des backends défaillants;
- DNS et TTL, mécanisme failover et caches des clients;
- certificats/API server name, CA et rotation;
- flux internes distincts du trafic externe;
- tests de perte d'un backend, puis du LB actif, sous contrat opérationnel.

Une configuration avec plusieurs DNS A records n'est pas nécessairement l'équivalent d'un LB HA : les comportements client, les retries et la stabilité des endpoints comptent.

## 13. Certificats : disponibilité et sécurité indissociables

L'API repose sur des identités TLS. Une erreur de trust CA peut conduire les clients à refuser une connexion, même si kube-apiserver et etcd sont sains. À l'inverse, contourner les vérifications TLS peut exposer des credentials et masquer un MITM ou une mauvaise configuration.

### 13.1 Chaîne de confiance

Pour un client API, quatre propriétés doivent être établies :
1. le nom demandé correspond aux SAN du certificat;
2. le certificat n'est pas expiré et son intervalle est valable;
3. sa chaîne remonte à une CA de confiance configurée;
4. le handshake et la politique crypto sont compatibles.

Le token OIDC ou kubeconfig n'est pas une solution à une erreur de SAN. Les interventions doivent cibler la couche responsable.

### 13.2 Rotation contrôlée

Une procédure de rotation doit vérifier la coexistence temporaire des anciens et nouveaux certificats, le renouvellement des composants dépendants, les caches de trust et les clients externes. L'objectif n'est pas seulement que le certificat soit signé, mais que les consommateurs **réels** continuent à établir des connexions fiables.

Les certificats et clés privées ne doivent pas être exportés dans le dépôt public. Une documentation peut montrer les champs non secrets : issuer, notBefore/notAfter, SANs anonymisés, identifiant d'autorité et dates de rotation.

## 14. Expérience HA : protocole en préproduction uniquement

On veut démontrer que la perte d'un nœud control plane n'empêche pas durablement l'API de traiter des écritures. Un test sérieux nécessite :

- environnement explicitement autorisé et HA supporté;
- baseline de santé et backup de control plane;
- mesure indépendante depuis au moins deux réseaux clients;
- définition d'un objet de test bénin dont l'écriture est approuvée;
- chronométrage du changement de leader et du rétablissement si applicable;
- mesures de latence p95/p99 et d'erreurs de l'API;
- suivi CVO, etcd et des control plane nodes;
- preuve d'intégrité des services après retour.

**Il est interdit d'exécuter ce protocole sur CRC partagé.** Un laboratoire mono-nœud permet d'étudier des objets, pas de valider le RTO d'une panne de master.

### 14.1 Rapport attendu

~~~text
ENV : 3 control-plane / 3 domaines physiques vérifiés
VERSION : OCP 4.22.x
MÉTHODE : panne contrôlée d'un membre (approval lié)
RÉSULTAT AVANT : API requests success / p99 / etcd health
RÉSULTAT PENDANT : nombre d'échecs / timeout / latence
RÉSULTAT APRÈS : majorité réelle, Operators, Pods, business SLI
DURÉE : horodatages UTC et méthode de calcul
RPO/RTO : valeurs observées, non supposées
LIMITES : dépendances non couvertes, systèmes externes
~~~

Il ne faut jamais attribuer un résultat PASS sans trace de test et un périmètre/version documentés.

## 15. Hosted control planes : nouvelle frontière, nouveaux risques

Lorsqu'un hosted control plane héberge les composants de contrôle sur un management cluster, le sort d'un tenant peut dépendre des Services et du réseau du management cluster. La séparation des workers n'implique pas l'indépendance des opérations de contrôle.

Comparer :
- contrôle des certificats et secrets;
- responsabilités des upgrades et des APIs;
- zone d'échec du management cluster;
- sécurité et séparation des tenants;
- coûts de support et capacité de récupération;
- backup et restauration spécifiques au modèle.

Un Hosted Control Plane ne remplace pas un plan de continuité.

## Sources complémentaires

- [Red Hat — Hosted Control Planes 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/hosted_control_planes/hcp-overview)
- [Red Hat — Backup/restore du control plane](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/backup_and_restore/control-plane-backup-and-restore)
