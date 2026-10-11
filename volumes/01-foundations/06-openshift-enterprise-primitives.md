# 06 — OpenShift en entreprise : RHCOS, Operators, Routes, SCC et gouvernance

**Volume 01 · EDITION_1_CONTENT_COMPLETE · Base : OpenShift Container Platform 4.22**  
**Statut documentaire : PUBLIC_VERIFIED ; aucune observation CRC nouvelle.**

## 1. Pourquoi une distribution Kubernetes intégrée ?

Kubernetes spécifie un ensemble d'API, de composants et de modèles de contrôleurs. Une plateforme d'entreprise doit aussi traiter l'installation des nœuds, l'authentification, l'évolution logicielle, l'observabilité, l'exposition réseau, la sécurité et le support opérationnel.

OpenShift livre un assemblage cohérent de ces fonctions, souvent opéré par des Operators. Cela réduit certains choix d'intégration, mais **n'externalise pas la responsabilité de l'architecte** concernant architecture applicative, IAM, clés, données, capacité, conformité et validation de reprise.

### Modèle de responsabilités

| Domaine | La plateforme apporte | L'équipe doit décider |
|---|---|---|
| API et control plane | Kubernetes/OCP et Operators associés | SLO de plateforme, topology, support et mises à jour |
| OS nœuds | RHCOS et cycle d'évolution intégré dans les configurations concernées | Cible d'installation, durcissement supporté, capacité |
| Réseau | CNI, DNS et fonctionnalités d'ingress | Zones de confiance, policies, noms DNS, flux tiers |
| Identité | Mécanismes d'authentification et de RBAC | Fournisseur d'identité, rôles, séparation des devoirs |
| Admission | SCC et autres contrôles | Contrats de workloads et exceptions |
| Monitoring | Stack et capacités d'observation | SLI/SLO applicatifs, conservation, alertes d'astreinte |
| GitOps | Composants possibles selon installation | Promotion, séparation des droits, stratégie de rollback |
| Données | Interfaces de volumes et intégration stockage | Sauvegarde, RPO/RTO, protection des données |

Une documentation produit décrit ce qui est possible, pas ce qui est automatiquement activé ou dimensionné sur un cluster particulier.

## 2. RHCOS et vie des nœuds

Red Hat Enterprise Linux CoreOS (RHCOS) est conçu pour héberger les composants de la plateforme et les charges conteneurisées; il comprend notamment kubelet et CRI-O. Les notes officielles de version **OpenShift Container Platform 4.22** exigent **RHCOS pour les nœuds control plane et compute**. Ne pas transposer à 4.22 les possibilités des anciennes versions.

**Ignition** fournit la configuration de première initialisation des machines. Le **Machine Config Operator** gère ensuite des changements de configuration du système selon les mécanismes prévus. Modifier manuellement un nœud en SSH pour régler durablement un incident introduit du drift et peut être écrasé par la gestion du cluster.

~~~mermaid
flowchart LR
  I[Installation / Ignition] --> N[État initial du nœud]
  M[MachineConfig / MCO] --> N
  N --> K[kubelet / CRI-O]
  K --> P[Pods]
  CV[Gestion des versions / CVO] --> M
  CV --> CO[Cluster Operators]
~~~

Le diagramme est une abstraction de responsabilités, pas le graphe d'ordonnancement réel de l'upgrade.

### Préflight read-only

~~~bash
oc get clusterversion
oc get nodes -o wide
oc get machineconfigpools
oc get clusteroperators
~~~

La présence d'un MCP Degraded ou d'un ClusterOperator Available=False requiert un diagnostic avant tout changement. Une mise à jour peut être inappropriée lorsque le cluster n'est pas sain.

## 3. Operators : deux familles et plusieurs contrats de gestion

Les **Cluster Operators** participent au fonctionnement de base de la plateforme et sont suivis par le Cluster Version Operator (CVO). Des **Operators additionnels** peuvent être gérés via Operator Lifecycle Manager (OLM) selon la version et le modèle d'installation. Il ne faut ni confondre la CRD métier d'un Operator applicatif avec un ClusterOperator, ni supposer que tout Operator sur le cluster est géré par OLM.

Pour un Operator applicatif, vérifier :

- API CRD et stabilité du contrat de version;
- validation à l'admission, idempotence et gestion des échecs;
- Conditions et Events utiles à l'exploitation;
- RBAC minimal, leader election si nécessaire;
- mécanisme de packaging/mise à jour;
- stratégie de suppression des ressources;
- preuve d'installation et de fonctionnement sur la cible.

Les Operators ne dispensent pas de l'analyse des modes de panne, des dépendances, des sauvegardes et de l'exploitation Day-2. Ces points seront traités en profondeur au Volume 08.

## 4. Authentification, autorisation et admission

Un utilisateur s'authentifie pour appeler les API. Les règles **RBAC** définissent ensuite les actions autorisées pour le sujet sur les ressources. Enfin, l'admission peut appliquer des validations ou mutations selon la politique de la plateforme.

Pipeline conceptuel :

~~~text
Identité et authentification
          ↓
Autorisation RBAC
          ↓
Admission (dont contraintes applicables)
          ↓
Validation et persistance API
          ↓
Boucle de réconciliation
~~~

L'ordre réel de certains traitements d'admission dépend de leur catégorie et de l'implémentation; le pipeline sert à structurer le raisonnement.

### SCC (Security Context Constraints)

Sur OpenShift, les SCC encadrent la possibilité de créer des Pods avec des paramètres de sécurité donnés. Elles peuvent limiter privilèges, UID, montages hostPath, capacités, accès aux namespaces hôte et d'autres champs. La politique effectivement utilisable dépend du service account et de ses droits.

Erreur fréquente : attribuer la SCC **privileged** pour éliminer un Permission denied. Cela change radicalement la frontière de sécurité et ne doit pas être une remédiation standard.

Inspection read-only :

~~~bash
oc -n NAMESPACE get serviceaccounts
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE describe pod NOM_POD
oc auth can-i create pods -n NAMESPACE
# Inspecter les SCC seulement si RBAC l'autorise :
oc get scc
~~~

**Attention** : `oc auth can-i create pods` ne prouve pas qu'un Pod arbitraire sera admis. L'admission SCC peut refuser la configuration particulière même lorsque l'utilisateur a les droits de créer la ressource. Les commandes `oc adm policy add-scc-to-user` ou équivalentes sont mutatrices et **exclues** de cet atelier.

## 5. Routes, Ingress et trafic entrant

Kubernetes définit la ressource **Ingress**; OpenShift fournit également les **Routes**, intégrées à son infrastructure d'ingress. Il faut distinguer :

- la **cible applicative**, exposée par un Service;
- le **contrat DNS/TLS**, porté par la Route ou l'Ingress selon design;
- le **routeur/controller**, qui met effectivement en œuvre l'exposition;
- les contrôles réseau qui limitent l'accès au trafic entrant et sortant.

Une Route avec un hôte connu n'assure pas qu'un backend est Ready; un certificat valide ne prouve pas la sécurité de l'API métier. Les modes de terminaison TLS et la capacité de passthrough/reencrypt nécessitent une configuration cohérente du trafic vers l'application.

~~~mermaid
flowchart LR
  CL[Client externe] --> DNS[DNS / VIP / LB]
  DNS --> IC[Ingress Controller / Route]
  IC --> S[Service]
  S --> A[Pod Ready]
  S --> B[Pod Ready]
~~~

Ce schéma ne détaille ni le traitement TLS, ni l'architecture de haute disponibilité du load balancer.

Diagnostic non destructif :

~~~bash
oc -n NAMESPACE get routes
oc -n NAMESPACE get svc
oc -n NAMESPACE get endpointslices
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE get networkpolicies
~~~

**Risques** : un OpenShift Route n'est pas le bon mécanisme universel pour tous les protocoles et flux non HTTP. Des alternatives comme un LoadBalancer peuvent être nécessaires en fonction des protocoles et de l'installation.

## 6. Réseau et sécurité : défense en profondeur

La présence d'un Service ne crée pas automatiquement une isolation de trafic. Les NetworkPolicies expriment des règles de sélection et d'autorisation des flux inter-Pods selon le dataplane et ses capacités. Une approche « default deny » doit être planifiée : le DNS, la télémétrie, les webhooks et les services nécessaires doivent rester autorisés.

Vue des frontières :

~~~text
Client externe
   │  réseau externe / DNS / firewall / LB
   ▼
Route / Ingress
   │  TLS et politiques d'exposition
   ▼
Service (sélection des endpoints)
   │  NetworkPolicy + réseau Pod
   ▼
Application
   │  OIDC, mTLS, token validation et contrôles métier
   ▼
Systèmes externes / base / messaging
~~~

Chaque ligne représente une responsabilité distincte. **NetworkPolicy ne remplace pas l'autorisation applicative.** De même, le chiffrement TLS du bord n'implique pas nécessairement un chiffrement de bout en bout jusqu'aux backends.

## 7. Observabilité et état de la plateforme

OpenShift expose des ressources et capacités de suivi de la plateforme. Il faut séparer **monitoring de cluster** et **monitoring des applications** : métriques infrastructure et ClusterOperators ne prouvent pas que le parcours métier fonctionne.

Trois niveaux d'observation :

1. **Nœuds et plateforme** : Ready, ClusterOperators, consommation, pression et erreurs système.
2. **Workloads** : Pods, restarts, scheduling, readiness, requests/limits, PVC.
3. **Service métier** : taux de succès des transactions, latence, backlog MQ, pertes de messages, disponibilité des dépendances.

Exemple d'un incident de paiement : le cluster peut être Ready, les Pods Running, mais le système de décision externe répondre trop lentement. La métrique de service doit permettre de distinguer la dégradation métier d'une panne d'orchestration.

## 8. CRC : excellente plateforme pédagogique, mauvaise preuve de HA

CodeReady Containers / OpenShift Local fournit une expérience OpenShift de laboratoire. Sur une installation locale mono-nœud, l'API, la couche applicative et les Workers peuvent partager un domaine de panne commun.

Cela permet de démontrer, selon les ressources disponibles : YAML, RBAC, SCC, Routes, Operators, certains contrôles GitOps et des scénarios applicatifs. Cela **ne valide pas** :

- tolérance à la panne d'un nœud indépendamment d'un autre;
- survie à la perte d'une zone physique;
- performances représentatives d'une plateforme bancaire de production;
- politiques d'upgrade et DR sur une topologie multinœuds;
- comportement sous trafic soutenu comparable à la production.

Un protocole expérimental avec preuve sur CRC peut toutefois prouver le **comportement observé sur CRC**, sans extrapolation.

## 9. Premier dossier d'architecture : exemple de banque

### Besoin

Exposer en HTTPS une API de consultation interne et relier son accès aux principes de moindre privilège, sans publier directement le middleware de paiement.

### Proposition (REFERENCE_ARCHITECTURE, non déployée)

- Projet applicatif isolé et contrôles RBAC par rôle.
- Service account dédié, image exécutée en non-root et compatible avec SCC.
- Deployment stateless à plusieurs replicas sur **des domaines de panne distincts en production**, si la plateforme les fournit.
- Service ClusterIP, Route/Ingress pour le seul point HTTP nécessaire.
- AuthN/AuthZ applicatives; segmentation de flux via NetworkPolicy validée.
- Logs structurés, traces corrélées, métriques techniques et transactionnelles.
- Requests/limits fondés sur mesures, probes conformes au comportement applicatif.
- Secret management, rotation, patching et stratégie de rollback.
- Plan de continuité couvrant dépendances et données; pas seulement les Pods.

### NFR à faire valider

| NFR | Indicateur | Validation attendue |
|---|---|---|
| Disponibilité | Succès de requêtes / période | Mesure end-to-end, panne contrôlée |
| Latence | p95/p99 de réponse | Test de charge représentatif |
| Isolation | Flux autorisés/refusés | Tests réseau négatifs et RBAC |
| Réversibilité | Temps de rollback | Drill versionné, incluant schémas de données |
| Audit | Traçabilité changement → artefact → déploiement | Provenance, logs et politique de rétention |
| Sobriété | CPU-seconde / transaction, énergie estimée | Baseline représentative et hypothèses transparentes |

Le SLA et les exigences réglementaires doivent être contractualisés avec le métier, RSSI et équipes d'exploitation; des nombres fictifs ne doivent pas être présentés comme engagements réels.

## 10. Questions d'architecte et anti-patterns

**Différence entre ClusterOperator et Operator OLM ?** Le premier fait partie des mécanismes de plateforme suivis par le CVO; le second est un modèle fréquent de gestion d'extensions. L'installation réelle et la prise en charge doivent être vérifiées.

**Un RBAC « create pods » suffit-il ?** Non : SCC, quota et politiques d'admission peuvent refuser une configuration.

**Une Route permet-elle de contourner un Service défaillant ?** Non : exposer un nom DNS ou une Route ne corrige pas l'absence de backend.

**Comment représenter CRC dans une démonstration de candidature ?** Comme laboratoire OpenShift local, avec version, limites de topologie, conditions de test et preuves ciblées.

**Que signifie « GitOps Healthy » ?** C'est un signal du contrôleur GitOps, pas une preuve complète de disponibilité métier ni de validation DR.

## Références

- [Red Hat OCP 4.22 — Release notes : Kubernetes 1.35, CRI-O, RHCOS control plane et compute](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes)

- [Red Hat — OCP 4.22 architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
- [Red Hat — OCP 4.22 control plane](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/control-plane)
- [Red Hat — OCP 4.22 routes](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/ingress_and_load_balancing/routes)
- [Red Hat — OCP 4.22 working with pods](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/nodes/working-with-pods)
- [Kubernetes — Application security](https://kubernetes.io/docs/concepts/security/application-security-checklist/)

**Revue restant ouverte** : vérifier les spécificités des versions et des Operators en environnement cible, puis compléter les séquences techniques au Volume 02 et les architectures réseau au Volume 04.
