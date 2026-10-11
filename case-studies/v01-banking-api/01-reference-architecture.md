# Étude de cas V01-C01 — API bancaire sur OpenShift : architecture de référence complète

**Statut : REFERENCE_ARCHITECTURE · Environnement : fictif, non déployé · Base : OCP 4.22**  
**Objectif : défendre une solution en comité d'architecture, sans prétendre avoir validé sa performance ou son HA.**

## 1. Besoin métier et hypothèses

Une banque souhaite exposer une **API de consultation de statut de paiement**, à des canaux internes et à des partenaires préalablement autorisés. Le service fournit un état au client mais ne doit pas créer de paiement dans ce parcours. Il interroge un référentiel de paiements et peut utiliser un système d'événements interne pour tracer les demandes.

**Hypothèses pédagogiques** : environnements distincts, cluster OpenShift d'entreprise, fournisseur d'identité OIDC, moteur applicatif HTTP, base de données externe au namespace de l'API et broker d'événements. La disponibilité effective, la classification de données, les seuils d'authentification, la rétention et les exigences DORA/RGPD doivent être définis avec les responsables concernés; aucun engagement règlementaire n'est supposé « acquis ».

### 1.1 Acteurs et responsabilités

| Acteur | Responsabilité principale | Ce qui lui est interdit par défaut |
|---|---|---|
| Client partenaire | Appeler l'API dans son périmètre | Lire d'autres clients ou namespaces |
| Fournisseur d'identité | Délivrer/valider une identité et les claims nécessaires | Déterminer seul la logique d'autorisation métier |
| API métier | Valider la requête, appliquer les autorisations, répondre | Accéder à des secrets d'autres applications |
| Base paiements | Source persistante de l'état du paiement | Être exposée directement sur l'ingress public |
| Broker | Découpler la publication de certains événements | Déduire une garantie exactly-once sans protocole |
| Plateforme | Héberger, sécuriser et observer les workloads | Se substituer aux validations métier |
| Sécurité/SRE | Définir contrôles, mesures et réaction incident | Traiter toute violation comme une simple relance Pod |

## 2. Architecture logique

~~~mermaid
flowchart TB
  EXT[Client autorisé] --> F[DNS / Pare-feu / Load Balancer]
  F --> R[Ingress Controller / Route]
  R --> S[Service ClusterIP]
  S --> A1[API Pod A]
  S --> A2[API Pod B]
  A1 --> ID[IdP OIDC / JWKS]
  A2 --> ID
  A1 --> DB[Référentiel paiements]
  A2 --> DB
  A1 --> MQ[Broker d'événements]
  A2 --> MQ
  A1 --> OT[Collector télémétrie]
  A2 --> OT
  PIPE[CI / SBOM / signatures] --> REG[Registry contrôlé]
  REG --> G[GitOps]
  G --> API[API OCP]
  API --> D[Deployment / Service / policies]
  D --> A1
  D --> A2
~~~

Il s'agit d'une vue logique. Les composants ne sont pas nécessairement dans le même cluster, et le diagramme ne représente pas les chemins de paquets, les autorités de certificats, les zones de sécurité ni la topologie de production.

### 2.1 Contrat entrant

La Route termine ou traverse TLS selon une décision explicite. Le certificat, le DNS, les noms de domaine, la relation avec le load balancer et les règles de redirection doivent être audités. La couche API ne doit pas accepter un simple en-tête `X-User` non authentifié comme identité de confiance. En présence d'un proxy, le contrat de confiance des headers `Forwarded` et `X-Forwarded-For` doit être documenté.

### 2.2 Authentification et autorisation

OIDC permet notamment la validation de tokens et l'intégration d'un fournisseur d'identité. Les décisions métier sont plus granulaires : un token techniquement valide n'autorise pas nécessairement l'accès à n'importe quel identifiant de paiement. Le service doit appliquer **l'autorisation objet par objet** et filtrer les données par périmètre de partenaire.

Critères testables : jeton absent → refus ; jeton expiré → refus ; issuer/audience erronés → refus ; token d'un autre partenaire → refus pour l'objet ciblé ; identifiant valide et droit accordé → réponse conforme. Les codes HTTP exacts dépendent du contrat API et de l'application; ils ne se déduisent pas automatiquement de Kubernetes.

### 2.3 Flux de données

Le référentiel de paiements peut être hors cluster. Son protocole, chiffrement, identité et stratégie de requêtes doivent être conçus indépendamment de la disponibilité des Pods. La publication d'événements est soumise à un contrat de duplication, d'acknowledgement, de retries et, si nécessaire, à un motif transactionnel comme l'outbox.

Si la réponse est une opération **de lecture**, un broker indisponible ne doit pas automatiquement transformer la lecture en nouvelle écriture métier répétée. Déterminer si la publication est facultative, exigée pour audit, différée ou bloquante. La bonne réponse dépend de l'obligation métier et réglementaire, pas de l'outil de messaging.

## 3. Contrôles OpenShift : défense en profondeur

### 3.1 Namespaces et service accounts

Un namespace ne représente pas, à lui seul, une frontière de sécurité absolue. La conception associe namespace, RBAC, SCC, NetworkPolicy, quotas, règles de secrets, audit et, selon la sensibilité, séparation par cluster. Les opérateurs humains et les service accounts applicatifs n'ont pas les mêmes droits.

Exemple d'objectif d'autorisation :

| Identité | Lecture des Pods | Création de Pods | Lecture des Secrets | Modification des SCC |
|---|---|---|---|---|
| Lecteur exploitation | Selon namespace | Non | Non | Non |
| Pipeline de livraison | Selon workflow | Seulement objets prévus | Selon mécanisme de livraison | Non |
| Runtime API | Le minimum opérationnel | Non | Seulement secrets montés explicitement, pas API générale | Non |
| Administrateur cluster | Selon procédure habilitée | Selon responsabilité | Accès soumis à contrôle fort | Exception gouvernée |

La dernière ligne n'est pas un appel à conserver des privilèges illimités; l'existence de droits élevés impose des approbations, audits et revues.

### 3.2 Admission et sécurité du Pod

Contraintes de conception : non-root, capabilities minimales, allowPrivilegeEscalation=false, seccomp adapté, volumes en écriture limités, pas de hostNetwork/hostPath sans justification formelle. Les règles SCC du cluster doivent confirmer l'admissibilité des images. Sur OCP 4.22, une SCC peut notamment contraindre l'UID, les capabilities et les accès privilégiés; elle ne remplace pas les politiques d'accès applicatives.

### 3.3 Segmentation réseau

Définir **l'intention de flux** avant d'écrire des NetworkPolicies. Exemple, à adapter aux adresses et identités des destinataires :

| Origine | Destination | Service | Motif |
|---|---|---|---|
| Ingress controller autorisé | API Pods | HTTP application | Trafic entrant |
| API Pods | DNS de cluster | DNS TCP/UDP | Résolution |
| API Pods | IdP / clés JWKS | HTTPS | Vérification de confiance |
| API Pods | Base paiements | Protocole base, port défini | Lecture métier |
| API Pods | Broker | Protocole messaging, port défini | Événements |
| API Pods | Collector télémétrie | Protocole telemetry | Logs/traces/métriques |

**Ne pas** assimiler des règles egress « restrictives » à un état sûr sans tests négatifs. Une résolution DNS cassée ou un flux TLS refusé peut rendre le service indisponible. Les spécificités OVN-Kubernetes et les politiques egress externes doivent être vérifiées selon version et topologie.

## 4. Disponibilité : distinguer cinq promesses

1. **Le Pod redémarre** après un crash de processus.
2. **Le Deployment conserve N réplicas souhaités** dans la mesure où le scheduler et les nœuds le permettent.
3. **La plateforme survit à un nœud** si les domaines de panne, capacités et composants concernés sont réellement redondants.
4. **Le service survit à une panne de dépendance** selon sa stratégie de timeout, cache, circuit-breaker et dégradation.
5. **Le métier tient son SLO** sur une période définie, mesuré au point de vue utilisateur.

Aucune de ces propositions ne découle automatiquement de la précédente. Sur CRC mono-nœud, seules des propriétés plus limitées peuvent être démontrées.

### 4.1 Couplages souvent cachés

- Deux Pods sur le même worker partagent un SPOF.
- Deux Pods sur deux workers peuvent dépendre du même volume incompatible avec le mode d'accès choisi.
- Deux bases en réplication peuvent partager la même alimentation, zone ou SAN.
- Une Route fonctionnelle peut dépendre d'un DNS externe non redondant.
- Une API à deux réplicas peut être bloquée par un unique service d'identité.
- Des retries non bornés peuvent amplifier une défaillance du système de décision.

## 5. Observabilité : du cluster à la transaction

Minimum de trois familles de SLI :

| Type | Signal | Condition de validité |
|---|---|---|
| Disponibilité | Proportion de consultations valides abouties sur période | Distinguer erreurs métier attendues et erreurs techniques |
| Latence | p95/p99 des demandes autorisées | Préciser point de mesure, fenêtres et exclusions |
| Intégrité fonctionnelle | Concordance de statut renvoyé avec la source | Corpus de référence contrôlé |

Signaux de diagnostic : taux de 5xx HTTP, latency par dépendance, nombre de Pods Ready, redémarrages, throttling CPU, erreurs SQL, backlog broker, épuisement de connexion, ratio de traces corrélées, saturation de pool.

Un SLO ne devient contractuel qu'après validation du métier et de l'exploitation. Pour illustration uniquement, 99,95 % de succès sur une période de **30 jours et sans exclusions** implique un budget de défaillance d'environ **21,6 minutes équivalentes**; selon la définition exacte des requêtes éligibles, les temps peuvent ne pas se traduire aussi simplement en minutes d'indisponibilité.

## 6. Livraison et rollback

Le chemin de déploiement doit lier **commit source → build → image digest → scan → attestation → approbation → manifeste GitOps → release**. L'objet affiché Synced n'est qu'un élément de la preuve. Pour revenir en arrière, étudier compatibilité des schémas de données, protocoles de messages, clients et migrations, et pas seulement l'ancien manifeste Kubernetes.

~~~mermaid
sequenceDiagram
  participant Dev as Développeur
  participant CI as CI/CD
  participant Reg as Registry
  participant Git as GitOps
  participant OCP as OpenShift
  participant Obs as Observabilité
  Dev->>CI: Commit validé
  CI->>CI: Tests, SBOM, politiques
  CI->>Reg: Image immuable référencée par digest
  CI->>Git: Proposition révision environnement
  Git->>OCP: Réconciliation contrôlée
  OCP->>Obs: Signals runtime
  Obs-->>Dev: Indicateurs de rollout et SLO
~~~

Aucun automatisme ne doit supprimer les contrôles de séparation de fonctions imposés dans un environnement sensible. Une promotion doit être traçable et, selon la politique interne, nécessiter approbation.

## 7. Critères d'acceptation du dossier

- Tous les flux métier documentés et testables.
- RBAC, SCC, NetworkPolicy et secrets raccordés aux identités réelles.
- ADR sur hébergement, zones, identité, données, rollout, rollback.
- SLI/SLO, dépendances et seuils validés par leurs responsables.
- Panne Pod/nœud/dépendance distinguées dans le plan de test.
- Capacity model incluant le mode dégradé et la réserve.
- Documentation des opérations Day-2 et réversibilité.
- Registre de preuves distinguant tests, observations et hypothèses.

**Aucune des validations ci-dessus n'a été exécutée dans cette étude de cas**. Voir le [runbook de diagnostic](02-n3-triage-and-evidence.md) et les [ADR et hypothèses de capacité](03-adr-and-sizing.md).

### Sources

- [Architecture OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [SCC OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/authentication_and_authorization/managing-pod-security-policies)
- [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Kubernetes Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
