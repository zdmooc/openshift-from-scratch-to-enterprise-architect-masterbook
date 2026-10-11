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
| CRD / API versioning | Chapitre 08 + L04 : CRD JSON à deux versions, ConversionReview, modèle et 20 tests | Confirmer cohérence du schéma avec un API server d'essai; vérifier storedVersions | OFFLINE_TESTS_A_VALIDER |
| Operators / OLM | Chapitre 12 : OLM Classic, OLM v1, CatalogSource/ClusterCatalog et ClusterExtension | Relecture des restrictions de support OLM v1 par package/version | RÉDIGÉ_À_VALIDER |
| HA / PKI / LB | Zones, TLS, quorum, hosted control planes, scénarios | Différencier disponibilité mesurée et topologie dessinée | REVOIR |
| Observabilité / N3 | Runbooks, cas fictifs, critères de preuve | Vérifier qu'aucun exemple n'est présenté comme incident réel; synthèse décisionnelle | REVOIR |
| Labs | 4 labs : quorum/scheduler/conversion CRD offline, inventaire read-only | Vérifier nouveaux tests L04 en CI; ne pas confondre simulation et runtime | QA_EN_COURS |
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
