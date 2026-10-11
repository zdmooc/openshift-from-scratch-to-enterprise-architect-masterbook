# Volume 02 — grille de clôture fondée sur le contenu

**Révision : 2026-10-11 · Évaluation provisoire de l'édition 1.1.**

La présence d'un PDF ne fait pas d'un livre une édition **FINAL**. Inversement, un document de 85 pages peut suffire à un périmètre donné si ses mécanismes sont bien traités. **Aucun quota de pages, de mots ou d'illustrations.**

## 1. Couverture technique et points à vérifier

| Domaine / attente lecteur | Couverture présente | Écart qualitatif ou validation à mener | État éditorial |
|---|---|---|---|
| Chemin d'une requête Kubernetes | API, authN/RBAC, admission, persistance, LIST/WATCH et APF | Contrôler les séquences et sémantiques OCP 4.22, illustrer les cas d'erreurs 409/410 | REVOIR |
| etcd / Raft / quorums | Consensus, majority, stockage, backup/restore, domaines de panne | Références de restore z-stream et procédures 4.22; aucune preuve DR | REVOIR |
| Scheduler / contrôleurs | Filters, scoring, priority, cache, workqueues et Lease | Comparer le simulateur offline aux règles réelles et documenter plugins/limites | REVOIR |
| CVO / OSUS | Release payload, graphes, conditions et upgrades | Vérifier chemins/compatibilités version 4.22; scénario de blocage détaillé | REVOIR |
| RHCOS / Ignition / MCO | Pools, rendered configs, node disruption policies | Clarifier les divergences documentaires Red Hat sur workers RHEL; approfondir les contraintes de mode de déploiement | REVOIR |
| Machine API | Chapitre 11 : Machine, MachineSet, ControlPlaneMachineSet, MHC et autoscaling | Vérifier chaque restriction provider/UPI et le statut Cluster API 4.22; relecture technique | RÉDIGÉ_À_VALIDER |
| kubelet / CRI-O / OCI | Container lifecycle, probes, UID, OOM, SIGTERM | Valider la cohérence des exemples et donner davantage de cas observables si nécessaire | REVOIR |
| SCC / PSA / webhooks | Contrats d'admission, service accounts et risques de politiques | Expliquer négatif/positif sur un manifest complet; statut non exécuté conservé | REVOIR |
| CRD / API versioning | Chapitre 08 + L04 : deux versions, ConversionReview, modèle à mapping total pour les états permis | Source officielle Kubernetes vérifiée : la conversion ne remplace pas l'admission; validation sur serveur réel absente | OFFLINE_TEST_PASS_API_PENDING |
| Operators / OLM | Chapitre 12 : OLM Classic et v1, ClusterExtension et contraintes de version confirmées par l'API 4.22 | Revue indépendante de compatibilité de packages spécifiques et installation réelle non réalisées | PUBLIC_VERIFIED_RUNTIME_PENDING |
| HA / PKI / LB | Zones, TLS, quorum, hosted control planes, scénarios | Différencier disponibilité mesurée et topologie dessinée | REVOIR |
| Observabilité / N3 | Runbooks, cas fictifs, critères de preuve | Vérifier qu'aucun exemple n'est présenté comme incident réel; synthèse décisionnelle | REVOIR |
| Labs | 6 labs : 3 modèles/contrôles offline et 3 lectures/exercices sans cluster | Nouveaux L05/L06 : scénarios de Machine API et OLM sur papier; aucune preuve runtime | DOCUMENTED_NOT_RUN / OFFLINE_TEST_PASS |
| Schémas | 4 SVG originaux, Mermaid en source | Contrôler sémantique et lisibilité; convertir autres schémas **seulement si cela clarifie le fond** | REVOIR |
| Sources / droits | Références officielles et politique mixte | Revue finale de versions, propriété des exemples et errata | REVOIR |

**Les statuts REVOIR ne signifient pas automatiquement que le chapitre doit s'allonger.** Une correction concise, un remplacement d'exemple ou une meilleure preuve peut suffire.

## 2. Critères pour déclarer l'édition FINAL

1. Le contenu promis par le périmètre du Volume 02 est couvert : API, etcd, scheduling, controller-manager, Operators, Machine API, CVO, MCO, RHCOS, CRI-O, sécurité d'admission, HA et N3.
2. Le lecteur peut répondre aux questions *quoi, pourquoi, comment, modes de panne, diagnostic, alternatives et limites* sans devoir deviner les mécanismes fondamentaux.
3. Les assertions sensibles à la version OCP 4.22 sont sourcées; divergences explicitées ou sorties du champ de certitude.
4. Les manifestes, commandes et figures sont cohérents, sûrs et correctement étiquetés (documentaires, non exécutés, offline, runtime).
5. Les laboratoires ont des objectifs, résultats attendus, cas négatifs et limites de représentativité.
6. Le PDF n'a pas d'erreurs bloquantes de navigation, de références ou de lisibilité; les droits d'auteur et les marques sont traités.
7. Les gates G1/G2/G4/G5 passent, et G3 uniquement lorsqu'une preuve runtime est effectivement revendiquée.

**Aucune exigence de 200, 280 ou 300 pages. Aucune rédaction de remplissage.**

## 3. Priorités de fond

**P0 — Pour la clôture technique :** les trois trous de contenu Machine API, OLM et CRD sont désormais rédigés avec leur propre contrat de preuve. Il reste la revue de compatibilité version 4.22, les validations de schéma et de conversion, la cohérence des cas/sources et l'édition du PDF une fois le fond accepté.

**P1 — Améliorations utiles si elles ajoutent des connaissances :** tests offline supplémentaires qui enseignent une propriété nouvelle, illustrations qui expliquent un mécanisme non évident, diagnostic de panne avec signaux discriminants.

**Hors périmètre de la clôture :** obtenir un nombre de pages, inventer des captures d'un cluster, effectuer un restore destructif, prétendre que CRC mono-nœud prouve une HA de production.

## 4. Verdict actuel

**VOLUME_02_EDITION_1_1_PUBLISHED — NOT_FINAL_PENDING_CONTENT_REVIEW.**

Il reste des sujets spécifiques et vérifiables à compléter. Le travail s'arrête quand ces sujets sont correctement couverts, **même si le volume conserve une pagination modeste**.

## 5. Contrôle CI après les nouveaux chapitres

Le [run GitHub Actions du 11 octobre 2026](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38155313628) est **SUCCESS** : 114 tests Python offline/éditoriaux réussis, 111 liens Markdown internes résolus. Ces résultats comprennent les 20 nouveaux tests de ConversionReview et les contrôles de structure des 12 chapitres. Ils ne valident pas une CRD sur un API server ni l'installation OLM/Machine API.

## 6. Corrections issues de l'audit de sources

- [OLM v1 4.22 : ClusterExtension API](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operatorhub_apis/clusterextension-olm-operatorframework-io-v1) : champs obligatoires et interaction entre channel, version et upgradeConstraintPolicy vérifiés ; ajout au chapitre 12.
- [Machine management 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/index) : MachineAutoscaler actif avec ClusterAutoscaler, MHC et support provider détaillés ; ajout au chapitre 11.
- [Kubernetes CRD conversion](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/) : une conversion ne doit pas servir de validation; l'échec peut bloquer des CR existantes; chapitre 08/lab L04 précisés.

Ces corrections qualifient les concepts documentés, **pas** les résultats runtime d'une installation ou du CRC.

## 7. Aperçu PDF complet vérifié — sans publication définitive

- [GitHub Actions — Content and PDF Preview](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38156129697) : **SUCCESS**.
- **12 chapitres et 6 labs** effectivement inclus; leurs titres figurent tous dans le texte extrait.
- 114 tests Python offline/structure réussis, 114 liens Markdown locaux résolus.
- PDF de prévisualisation : texte extractible (229871 caractères), fichier 403423 octets. La pagination est informative seulement.
- Les contrôles CI ne constituent pas une revue indépendante complète de chaque commande ou une certification du support pour tous les providers.
- Le dernier PDF public **1.1 reste inchangé**; l'aperçu sert à détecter les problèmes de composition avant décision de clôture basée sur C1–C7.

### Verdict actualisé

**CONTENT_SCOPE_12_CHAPTERS_6_LABS — SOURCE_CHECKED_KEY_CONTRACTS — PREVIEW_PDF_PASS — FINAL_REVIEW_PENDING.**

Les P0 « rédiger Machine API », « rédiger OLM » et « fournir un vrai exemple CRD » sont résolus sur le plan du contenu. Les réserves suivantes restent explicites : contradiction documentaire RHEL worker 4.22, compatibilité exacte avec les différents providers et packages, absence de test d'admission/convert webhook sur API server, et relecture éditoriale finale des 12 chapitres.
