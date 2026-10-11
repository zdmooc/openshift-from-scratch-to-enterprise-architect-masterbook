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
