# Catalogue des dépôts et des preuves

> Cet inventaire est un **point d'entrée éditorial** basé sur des travaux rapportés. Les preuves doivent être vérifiées dans leurs dépôts avant de monter une affirmation au niveau RUNTIME_PROVEN dans le livre. Aucun runtime n'a été testé par cette initialisation.

| Programme | Dépôt source | Matières à réutiliser | Volumes | Statut dans ce masterbook |
|---|---|---|---|---|
| D-091 Instant Payments | [mayabank-instant-payments-resilience-platform](https://github.com/zdmooc/mayabank-instant-payments-resilience-platform) | Argo CD, sync, drift, self-heal, prune, rollback, observabilité, segmentation | 06, 07, 09, 10 | EVIDENCE_REVIEW_REQUIRED |
| D-093 Platform Operator | [shared-platform-services-openshift](https://github.com/zdmooc/shared-platform-services-openshift) | Operator Go, SSA, CRD, conditions, métriques, leader election, Day-2 | 02, 08, 09, 11 | EVIDENCE_REVIEW_REQUIRED |
| D-090 TradeOps | [TradeOps-GenAI-Integration](https://github.com/zdmooc/TradeOps-GenAI-Integration) | Intégration API/EDA, observabilité, MQ et gouvernance runtime | 07, 09, 12 | EVIDENCE_REVIEW_REQUIRED |
| D-100 consolidation | Dépôt de cadrage à retrouver et confirmer | IDP/Backstage, secrets, CI/CD, supply chain, backup/restore, upgrades | 06, 07, 10, 11 | COVERAGE_AND_GATES_TO_VERIFY |
| MQ/EDA platform | [mayabank-ibm-mq-native-ha-openshift-eda-platform](https://github.com/zdmooc/mayabank-ibm-mq-native-ha-openshift-eda-platform) | Messaging, HA, intégration événementielle | 10, 12 | EVIDENCE_REVIEW_REQUIRED |
| AI Infrastructure | [enterprise-ai-infrastructure-reference-architecture](https://github.com/zdmooc/enterprise-ai-infrastructure-reference-architecture) | CPU/GPU, dimensionnement, multicloud, FinOps/Green IT | 11, 12 | REFERENCE_REVIEW_REQUIRED |

## Processus de promotion d'une preuve

1. Identifier commit SHA, branche et chemin précis dans le dépôt source.
2. Identifier version du cluster, date, périmètre et protocole de mesure.
3. Distinguer sortie d'outil, succès de script, test automatisé et comportement observé.
4. Enregistrer résultat, limites et possibilité de reproduction.
5. Associer la preuve à une assertion spécifique du chapitre.
6. Protéger les données sensibles avant toute publication.
7. Réviser le statut de preuve dans le chapitre et dans ce catalogue.

## CRC — référence historique, non contrôle actuel

Un environnement de lab OpenShift 4.22.7 sur CRC a été rapporté en octobre 2026. Cette information constitue **un contexte historique**, pas une vérification du cluster au 11/10/2026. Aucune commande de modification ni de capture nouvelle n'est nécessaire pour le cadrage.

## Anti-duplication

Le masterbook **résume, explique et référence** les preuves des dépôts sources. Les scripts et manifestes de déploiement restent chez leurs propriétaires. Toute réutilisation d'un bloc doit être attribuée et examinée pour compatibilité des licences.
