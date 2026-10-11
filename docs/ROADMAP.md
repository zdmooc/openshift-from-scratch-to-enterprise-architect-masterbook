# Roadmap d'édition du Masterbook

**Date de référence : 2026-10-11** · **Découpage initial, non contractuel**

## Itérations structurantes

| ID | Objet | Critère de sortie | État |
|---|---|---|---|
| OCP-MB-I0 | Dépôt, cadrage, structure, licences, preuves | README, charte, index, référence V01 | CLOSED (cadrage initial) |
| OCP-MB-I1 | V01 plan + chapitres de base | 11 chapitres en brouillon, 3 études de cas, revue technique restante | ELEVEN_CHAPTERS_DRAFTED_QA_PENDING |
| OCP-MB-I2 | V01 labs et questions d'architecture | 8 fiches, 42 tests Python offline PASS ; CRC non testé | OFFLINE_TESTS_PASS_CRC_PENDING |
| OCP-MB-I3 | V02 architecture interne | Mécanismes, schémas et sources | PLANNED |
| OCP-MB-I4 | V03 installation/administration | Topologies et procédures vérifiées | PLANNED |
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
| OCP-MB-I15 | Génération de l'édition | Build PDF/EPUB + G5 | PLANNED |

Une ligne n'équivaut pas à une unique session : chaque volume est un **lot** comportant autant d'itérations d'écriture, revue et tests que nécessaire. Aucun engagement de pages ou de clôture sans contenu vérifié.

## Ordre recommandé par valeur

1. V01 et V02 : langage et architecture.
2. V08 et V07 : démonstrations existantes D-093 et D-091, rapidement valorisables en entretien.
3. V09 et V06 : SRE/N3 et security.
4. V03/V04/V05/V10 : couverture exploitation de plateforme.
5. V11/V12 : architecture d'entreprise, IA et Green IT.

**Contraintes CRC** : pas de nouveaux labs lourds tant que le cluster local est contraint. Privilégier les preuves historiques, les schémas, les lectures seules et la documentation de référence, avec statut correspondant.

## Étape immédiatement suivante

OCP-MB-I1 : approfondir les cas pratiques réels, ajouter des exercices testables sans CRC, revoir les chapitres et sources puis valider techniquement les labs dans un environnement autorisé. Le chapitre rédigé ne vaut pas contenu éditorial final.
