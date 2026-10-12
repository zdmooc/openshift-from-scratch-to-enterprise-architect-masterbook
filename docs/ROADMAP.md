# Roadmap d'édition du Masterbook

**Date de référence : 2026-10-12** · **Découpage initial, non contractuel** · **Critères de fin : contenu, pas pages**

## Itérations structurantes

| ID | Objet | Critère de sortie | État |
|---|---|---|---|
| OCP-MB-I0 | Dépôt, cadrage, structure, licences, preuves | README, charte, index, référence V01 | CLOSED (cadrage initial) |
| OCP-MB-I1 | V01 plan + chapitres de base | 13 chapitres + 3 cas, édition contenu complète | EDITION_1_CONTENT_COMPLETE |
| OCP-MB-I2 | V01 labs et questions d'architecture | 8 labs, 42 tests offline PASS ; runtime non revendiqué | OFFLINE_TESTS_PASS |
| OCP-MB-I3 | V02 architecture interne | 12 chapitres, 6 labs, audit technique, PDF 1.3 contrôlé | CLOSED_DOCUMENTARY_SCOPE |
| OCP-MB-I4 | V03 installation/administration | Topologies et procédures à rédiger et contrôler | IN_PROGRESS |
| OCP-MB-I5 | V04 réseaux | Architecture des flux + diagnostics | PLANNED |
| OCP-MB-I6 | V05 storage/data | Workloads stateful + RPO/RTO | PLANNED |
| OCP-MB-I7 | V06 sécurité | Modèle menaces + contrôles | PLANNED |
| OCP-MB-I8 | V07 GitOps/DevSecOps | Chaîne de livraison et preuves | PLANNED |
| OCP-MB-I9 | V08 Operators | Go/Kubebuilder/Day-2 | PLANNED |
| OCP-MB-I10 | V09 SRE/N3 | Runbooks et analyse incidents | PLANNED |
| OCP-MB-I11 | V10 HA/DR/multicluster | Scénarios de défaillance et restore | PLANNED |
| OCP-MB-I12 | V11 IDP/FinOps/Green IT | Modèle plateforme et mesures | PLANNED |
| OCP-MB-I13 | V12 Advanced | Cas sectoriels/IA/VM | PLANNED |
| OCP-MB-I14 | QA transverse, glossaire, index | Contrôles G1–G4 et liens | PLANNED |
| OCP-MB-I15 | Génération de l'édition | PDF Volume 01 publié et vérifié, EPUB ultérieur | PDF_V01_PUBLISHED |

Une ligne n'équivaut pas à une unique session : chaque volume est un **lot** comportant autant d'itérations d'écriture, revue et tests que nécessaire. Aucun engagement de pages ou de clôture sans contenu vérifié.

## Ordre recommandé par valeur

1. V01 et V02 : langage et architecture.
2. V08 et V07 : démonstrations existantes D-093 et D-091, rapidement valorisables en entretien.
3. V09 et V06 : SRE/N3 et security.
4. V03/V04/V05/V10 : couverture exploitation de plateforme.
5. V11/V12 : architecture d'entreprise, IA et Green IT.

**Contraintes CRC** : pas de nouveaux labs lourds tant que le cluster local est contraint. Privilégier les preuves historiques, les schémas, les lectures seules et la documentation de référence, avec statut correspondant.

## Statut actuel et prochaine étape

**Volume 02 : CLOSED_DOCUMENTARY_SCOPE.** La [publication PDF 1.3](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.3-20261012) a réussi ses [contrôles CI](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38217687784) : 117 tests, 125 liens Markdown, texte et sections du PDF, et contrôle spécifique du glossaire. La dernière page a été vérifiée visuellement après correction du tableau. Aucune preuve runtime de HA/PRA ni d'installation d'Operator n'est revendiquée.

**Volume 03 : IN_PROGRESS**, sur [installation et Day-1](../volumes/03-install-operate/README.md). La rédaction suit les matrices officielles OCP 4.22, sans lancer de nouvelle charge sur le CRC.

**Critère de fin :** qualité et couverture du contenu, jamais nombre de pages.
