# V02-C01 — Dossier d'architecture : control plane OpenShift bancaire

**Statut : REFERENCE_ARCHITECTURE · Scénario fictif · Aucun déploiement ni test de panne**

## 1. Contexte

Une banque possède un cluster OpenShift hébergeant des APIs de consultation de paiements, plusieurs services de messagerie et une chaîne GitOps. Elle doit définir le niveau de support du control plane, sa capacité à supporter les mises à jour et son protocole de retour au service en cas d'incident.

La solution ne peut être conclue à partir de la seule existence de trois masters ou de Pods Ready. Elle dépend de l'architecture physique, des identités, du LB, d'etcd, des capacités des nœuds et de la disponibilité des services métier.

## 2. Cartographie des responsabilités

| Domaine | Responsable pressenti | Preuve |
|---|---|---|
| OCP/CVO | Équipe Platform Engineering | ClusterVersion, release, runbooks |
| RHCOS/MCO | Équipe plateforme / infrastructure | MCP, rendered configs, maintenance |
| etcd/quorum | Équipe cluster habilitée | Health, backup, exercice de reprise |
| DNS/LB/certificats | Réseau, infrastructure et PKI | Reachability, tests TLS |
| Add-on Operators | Propriétaire du service | Matrice de compatibilité |
| Applications | Équipes produit | SLI/SLO métier |
| Incidents | SRE/Support N3 | Runbooks, journaux expurgés, escalade |
| Gouvernance | Responsable SI et RSSI | ADR, approvals, classification de données |

## 3. Choix de topologie

**Option A : cluster mono-nœud de laboratoire.** Adapté à l'apprentissage des APIs, de GitOps et des contrôles, sans prétention HA.

**Option B : cluster OCP production supporté avec trois nœuds de contrôle.** Nécessite de valider les domaines de panne, LB, réseau inter-membres et stockage d'etcd. La faisabilité dépend de la plateforme et des matrices support Red Hat.

**Option C : hosted control plane.** Déplace des responsabilités d'hébergement vers une infrastructure de management et nécessite une analyse du blast radius, de la sécurité, du réseau et du PRA du management cluster.

La décision dépend des exigences de sécurité, de support, de coût complet et de résilience, pas d'un classement universel.

## 4. ADR-001 : aucune intervention manuelle durable sur RHCOS

**Décision de référence :** changements système via mécanismes supportés et gestion de configuration MCO.  
**Motif :** éviter dérive SSH, incohérences de nœuds, maintenance non reproductible.  
**Risque :** rendu MachineConfig incorrect et rollouts de nœuds non préparés.  
**Preuve :** validation en environnement de préproduction, MCP convergé et calendrier de maintenance.

## 5. ADR-002 : update via recommandations supportées

**Décision :** utiliser CVO et graphes recommandés, valider préflight et sauvegardes avant toute mise à jour.  
**Motif :** compatibilité du payload et des Operators.  
**Risque :** régression de CRD/add-on ou impossibilité de revenir à la version précédente.  
**Preuve :** logs CVO, conditions, SLI applicatifs pré/post update et compte rendu.

## 6. ADR-003 : séparation des privilèges API et des exceptions

**Décision :** RBAC minimal, SCC appropriées aux ServiceAccounts, PSA et webhooks définis comme contrats de plateforme.  
**Motif :** empêcher qu'une création Pod compromette le système hôte.  
**Risque :** policy ou webhook indisponible bloquant une création légitime.  
**Preuve :** tests positifs et négatifs d'admission, tests de reprise de webhook.

## 7. Plan de qualification de la résilience

| Scénario | Impact à mesurer | Prérequis |
|---|---|---|
| Panne contrôlée d'un nœud de contrôle | API read/write, quorum et scheduling | HA multinœud, sauvegarde, autorisation |
| Perte du LB principal | Accès API de réseaux clients | Architecture de redondance du LB |
| Échec de renouvellement de certificat | TLS client/API | PKI de test, contrôle identité |
| Panne d'un webhook | Créations de Pod, admissions | Sandbox et plan de recovery |
| Rollout MCO lent | Pods évincés, capacité restante | PDB, spare capacity, supervision |
| Augmentation latence etcd | p95/p99 API et erreur | Métriques disque, isolation et rollback |
| Restauration après incident | RTO/RPO et intégrité du cluster | Procédure Red Hat, environnement distinct |

Aucun résultat n'est enregistré comme PASS. Chaque protocole exige un propriétaire, une preuve et un statut RUNTIME_PROVEN seulement après exécution.

## 8. Questions pour le comité d'architecture

1. Que survit-il à la perte du domaine de panne majeur ?
2. Quelle est la chaîne exacte DNS/LB/certificats/API/etcd ?
3. Le backup etcd peut-il être restauré avec la bonne z-stream ?
4. Quels changes MCO nécessitent drain/reboot ?
5. Comment les Operators add-on sont-ils vérifiés avant la release ?
6. Le SLO d'une transaction bancaire est-il mesuré indépendamment des Conditions Kubernetes ?
7. Quel protocole interdit qu'une panne de control plane mène à une modification improvisée ?
8. Comment vérifier la séparation entre sujets humains et ServiceAccounts de workloads ?

## 9. Conclusion

L'architecture cible est acceptable seulement lorsque les hypothèses critiques (domaines de panne, sauvegarde, état des certs, admission, MAJ, SLO) deviennent des propriétés mesurables. Le dossier constitue une **architecture de référence**, non une homologation ni un résultat runtime.


## 10. Matrice d'impacts croisés : control plane, applications et SI externe

Dans une architecture bancaire, le périmètre « OpenShift » n'est pas une frontière suffisante pour qualifier l'impact d'un incident. Une même panne de domaine peut toucher le control plane, les workers, le registre d'images, le système de décision, les bases et les chemins réseau.

| Domaine de panne | Control plane | Workloads existants | Capacité de remplacement | Données métier |
|---|---|---|---|---|
| Un worker | API généralement indépendante | Pods du worker affectés | Dépend des autres workers | CSI/DB selon design |
| Un master (HA) | Majorité etcd à confirmer | Souvent processus existants inchangés | Dépend de l'API/scheduler | Dépendances externes |
| Endpoint API / LB | Clients API ne rejoignent plus l'endpoint | Certains traitements continuent | Déploiements/ops perturbés | Peut continuer |
| CA / DNS | TLS/résolution clients erronés | Effets selon dépendances | Rollouts et pulls possibles affectés | Propagation fonctionnelle |
| Storage backend commun | etcd/PVs potentiellement affectés | I/O et états perturbés | CSI/attach perturbé | Risque d'intégrité élevé |
| Broker externe | Control plane potentiellement sain | Consumers en erreur | Nouveaux Pods parfois sans effet | Backlog/doublons |
| IdP externe | API OCP et authN métiers peuvent varier | Requêtes protégées affectées | Dépend des credentials | Risque de refus/indisponibilité |

Cette matrice est une hypothèse de référence. Chaque application peut réagir différemment selon le mode de connexion, les caches, les timeouts et les stratégies de retry.

## 11. Calcul de capacité après perte d'une zone (papier)

Scénario totalement fictif :
- 3 zones;
- 6 workers de 8 CPU allocatables (2 par zone);
- demande applicative totale de 30 CPU répartie à parts égales;
- demande système/Daemons par worker de 1 CPU supposée incluse **séparément**.

Capacité CPU totale après perte d'une zone : 4 workers × 8 CPU = 32 CPU allocatables. Si la demande applicative est toujours 30 CPU et les DaemonSets exigent 4 CPU supplémentaires sur les survivors, le total demandé devient 34 CPU. Le cluster **ne peut pas replacer toute la demande** malgré ses 32 CPU disponibles.

Ce calcul ne valide pas non plus l'équilibre mémoire, les volumes et le nombre de Pods. En production, il faudrait une réserve plus large et des mesures de p95/p99 en mode dégradé.

## 12. Plan de tests de reprise et preuves

| Test | Dépendances | Critère |
|---|---|---|
| Panne worker | Cluster multinoeud autorisé | Endpoints / SLI rétablis |
| Panne master | Quorum, LB, autorisation | API read/write maintenues ou restaurées |
| Perte LB | Redondance d'API | Clients retrouvent endpoint dans RTO |
| Échec admission webhook | CA/service/selector | Reprise de création sans élargir sécurité |
| Upgrade MCO | PDB et capacité | Rollout convergé sans dépasser error budget |
| Restore etcd | Sauvegarde/version/z-stream | État API restauré et cohérent |
| Reprise base/broker | Backups/offsets/idempotence | Transactions intègres, pas de pertes inconnues |

Ce plan ne constitue **pas** une validation. Les essais destructifs doivent rester sous contrôle strict sur des environnements isolés, avec backups vérifiés et acteurs habilités.

## 13. Registre des décisions à approuver

1. Topologie supportée et indépendance physique des zones.
2. Responsabilité du load balancing et des certificats API.
3. Stratégie de backup etcd et conditions de version de restauration.
4. Politique de gestion des MachineConfigs, rollouts et PDB.
5. Compatibilité de CRD et d'Operators additionnels.
6. Politique d'admission de sécurité et disponibilité des webhooks.
7. Responsabilité de validation du SLO métier et de l'intégrité des données.
8. Procédure de support N3, chaîne d'escalade et preuve d'incident.
9. Politique de sobriété, dimensions de capacité réservée et coût de résilience.

Un dossier est prêt à être soumis en comité seulement si les décisions sont accompagnées de risques, responsables, échéances et méthodes de preuve. Le présent exemple reste une architecture de référence.
