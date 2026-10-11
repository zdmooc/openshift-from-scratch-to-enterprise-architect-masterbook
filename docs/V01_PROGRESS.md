# Volume 01 — état réel de publication (2026-10-11)

## Matrice de couverture

| Sujet | Chapitre | Preuve | État |
|---|---|---|---|
| Positionnement conteneurs/Kubernetes/OCP | 01 | Documentation officielle | DRAFT |
| Desired state, reconcile, controller/Operator | 02 | Documentation officielle | DRAFT |
| Linux namespaces, cgroup v2, sécurité | 03 | Kernel docs + Kubernetes | DRAFT |
| OCI image, manifest, runtime, distribution | 04 | OCI specifications | DRAFT |
| API objects, Deployment, scheduling, Services | 05 | Kubernetes docs | DRAFT |
| Particularités RHCOS, SCC, CVO, Routes | 06 | Red Hat 4.22 | DRAFT |
| Évaluation, cas métier, 25 questions | 07 | Raisonnement et corrigés éditoriaux | DRAFT |
| Observation cluster / Linux / OCI / API | Labs L01–L04 | Procédures uniquement | DOCUMENTED_NOT_RUN |
| Revue d'architecture de paiements | Lab L05 | Exercice sur papier | REFERENCE_ARCHITECTURE |

## Limites actuelles

- La **rédaction initiale** de sept chapitres est faite; elle est loin d'une édition illustrée de 180–240 pages.
- Aucun lab n'a été relancé sur CRC au cours de cette itération.
- Les extraits de manifeste utilisant registry.example.invalid et des digests fictifs sont **non déployables**; ils servent de supports de conception.
- Les mécanismes d'admission et la compatibilité doivent être revus selon la version OpenShift cible.
- La couverture testée de la sécurité de l'image, des architectures multi-nœuds et des restaurations est hors périmètre V01.
- La politique de licences définitive demeure ouverte.
- Les chapitres 01/02, plus introductifs, devront être enrichis pour une cohérence de profondeur avec 03–06.

## Restant avant V01 FINAL

1. Consolider les sources au niveau de chaque affirmation critique.
2. Faire relire exactitude Kubernetes/OpenShift et exemples YAML.
3. Compléter les chapitres par séquences approfondies, cas pratiques et anti-patterns.
4. Tester les commandes sur un environnement autorisé et consigner date/version/limitations.
5. Vérifier les liens, figures et licences.
6. Bâtir et relire une édition structurée PDF/EPUB, uniquement après gates éditoriaux.

## État des travaux

OCP-MB-I0 **CLOSED (cadrage)** ; OCP-MB-I1 **CONTENT_DRAFTED_QA_PENDING** ; OCP-MB-I2 **LABS_DOCUMENTED_VALIDATION_PENDING**. Il reste de la rédaction et des vérifications substantielles pour fermer le Volume 01.
