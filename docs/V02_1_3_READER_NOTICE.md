# Avis au lecteur — Volume 02, édition 1.3

**Ouvrage indépendant, © 2026 Zidane Djamal pour ses créations originales. Tous droits réservés dans cette édition en l'absence de licence particulière.** OpenShift et Red Hat sont des marques de leurs propriétaires; ce livre n'est ni un guide officiel Red Hat ni une certification.

## Périmètre

L'ouvrage explique les mécanismes internes d'OpenShift Container Platform 4.22, son control plane et ses Operators; il ne prescrit pas un runbook de production universel. L'installation concrète, les opérations HA/DR et les configurations propres aux providers dépendent de guides de support applicables à la version exacte et à l'environnement.

## État des preuves

Les laboratoires comprennent des **simulations Python hors cluster**, des **exercices sur papier** et des **commandes de lecture seule documentées non exécutées**. Aucun changement, upgrade, panne injectée, intervention sur etcd, installation d'Operator ou manipulation de Machine API n'a été exécuté sur le CRC lors de la rédaction.

**La réussite de tests Python ne prouve pas le fonctionnement d'un composant Kubernetes réel.** Aucun RTO/RPO, SLA, certification ou résultat de conformité n'est revendiqué.

## Erratum lié au support des workers

La documentation officielle OpenShift 4.22 contient des indications à rapprocher concernant la prise en charge éventuelle de workers RHEL, tandis que le plan de contrôle s'appuie sur RHCOS dans les installations habituelles. Une validation de support dépend du provider, du mode d'installation et de la version. Consulter le registre d'erratum dans le dépôt avant d'architecturer une solution client.

## Sources et pérennité

Ce livre est daté du 12 octobre 2026, cite des sources officielles en ligne et peut être corrigé dans de futures éditions. Les sources Markdown versionnées, les scripts de construction et les notes de publication assurent la traçabilité. Le nombre de pages n'a aucun rôle dans la décision de complétude.
