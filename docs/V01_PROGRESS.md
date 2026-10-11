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
| Admission SCC/PSA, Routes TLS et NetworkPolicy | 08 | Red Hat OCP 4.22 + Kubernetes | DRAFT |
| Réseau DNS/Service/Ingress et diagnostic | 09 | Red Hat 4.22 DNS/networking + Kubernetes | DRAFT |
| Stockage PVC/PV/CSI et restore | 10 | Kubernetes Storage + OCP 4.22 | DRAFT |
| Diagnostic N3 et preuve causale | 11 | Méthodologie et API Kubernetes | DRAFT |
| Observation cluster / Linux / OCI / API | Labs L01–L04 | Procédures uniquement | DOCUMENTED_NOT_RUN |
| Revue d'architecture de paiements | Lab L05 | Exercice sur papier | REFERENCE_ARCHITECTURE |
| Simulation d'un contrôleur | Lab L06 + code + 10 tests Python | GitHub Actions, exécution offline | OFFLINE_TESTS_PASS |
| Manifests inter-reliés, SCC/PSA/Route/Policy | Lab L07 + 6 objets JSON + 14 tests Python | GitHub Actions, exécution offline | OFFLINE_TESTS_PASS |
| Triage offline N3 | Lab L08 + 4 cas JSON + 18 tests Python | GitHub Actions, exécution offline | OFFLINE_TESTS_PASS |
| Architecture bancaire, runbook N3, ADR | C01–C03 | Dossier fictif, analyses et scénarios | REFERENCE_ARCHITECTURE |

## Limites actuelles

- La **rédaction initiale** de onze chapitres est faite; elle est loin d'une édition illustrée de 180–240 pages.
- Aucun lab n'a été relancé sur CRC au cours de cette itération. Les 42 tests offline (10 reconcile + 14 manifest + 18 triage) sont passés dans GitHub Actions, sans prouver une exécution sur OpenShift.
- Les extraits de manifeste utilisant registry.example.invalid et des digests fictifs sont **non déployables**; ils servent de supports de conception.
- Les mécanismes d'admission et la compatibilité doivent être revus selon la version OpenShift cible.
- La couverture testée de la sécurité de l'image, des architectures multi-nœuds et des restaurations est hors périmètre V01.
- La politique de licences définitive demeure ouverte.
- Chapitres 01/02 enrichis sur responsabilité, dimensionnement, réconciliation, field ownership et Day-2. Ils requièrent encore revue technique et densification avant une édition de 180–240 pages.

## Exécution automatisée vérifiée

- [Workflow GitHub Actions vert (42 tests Python + liens internes)](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38133097928).
- Portée : environnement GitHub Actions Ubuntu, tests du simulateur pédagogique et présence des fichiers ciblés par les liens Markdown.
- Les dossiers C01–C03, l'index et les liens locaux sont inclus dans les vérifications automatiques. La CI ne valide pas les liens externes, les schémas Kubernetes côté serveur ni les tests runtime.

## Restant avant V01 FINAL

1. Consolider les sources au niveau de chaque affirmation critique.
2. Faire relire exactitude Kubernetes/OpenShift et exemples YAML.
3. Compléter les chapitres par séquences approfondies, cas pratiques et anti-patterns.
4. Tester les commandes sur un environnement autorisé et consigner date/version/limitations.
5. Vérifier les liens, figures et licences.
6. Bâtir et relire une édition structurée PDF/EPUB, uniquement après gates éditoriaux.

## État des travaux

OCP-MB-I0 **CLOSED (cadrage)** ; OCP-MB-I1 **ELEVEN_CHAPTERS_DRAFTED_QA_PENDING** ; OCP-MB-I2 **FORTY_TWO_OFFLINE_TESTS_PASS_CRC_VALIDATION_PENDING**. Il reste de la rédaction et des vérifications substantielles pour fermer le Volume 01.
