# Volume 02 — Rapport de revue technique et éditoriale

**Date : 12 octobre 2026 · Cible documentaire : OpenShift Container Platform 4.22 et Kubernetes 1.35.**
**Périmètre : 12 chapitres, 6 ateliers, 1 étude d'architecture, 4 schémas SVG originaux.**
**Niveau de conclusion : COMPLET POUR LE PÉRIMÈTRE DOCUMENTAIRE. Aucun test runtime nouveau.**

## Décision de clôture (qualité du contenu, non pagination)

| Critère de sortie | Conclusion | Limites |
|---|---|---|
| C1 Couverture | PASS : API/etcd, scheduler, CVO, MCO, CRI-O, admission, CRD, Machine API, OLM Classic/v1, HA et N3 | Installation pratique détaillée réservée au volume 03 |
| C2 Profondeur | PASS : mécanismes, frontières de responsabilité, scénarios de pannes, diagnostics, exercices et ADR | Les exercices papier ne reproduisent pas les systèmes réels |
| C3 Sources et compatibilité | PASS_WITH_CAVEAT : assertions 4.22 clés revues et corrections enregistrées | Documentation Red Hat divergente sur l'OS de certains workers : erratum maintenu |
| C4 Reproductibilité | PASS_DOCUMENTARY : exemples Python et tests offline, procédures lecture seule | Pas d'admission Kubernetes, de webhook TLS ni de déploiement OLM |
| C5 Statut des preuves | PASS : sources, simulations et scénarios identifiés; aucun RUNTIME_PROVEN inventé | HA, DR et upgrade ne sont pas testés |
| C6 Droits et sécurité | PASS_PUBLICATION_WITH_RESERVED_RIGHTS : textes/figures originaux, citations de liens, pas de dump d'environnement | Licences mixtes de réutilisation à formaliser séparément; aucune licence ouverte présumée |
| C7 Publication | À valider par CI de l'édition 1.2 : PDF, texte, pages, figures, liens, navigation | Ne pas publier sur échec de CI |

Une édition documentaire techniquement close peut conserver des **limites de preuve runtime**. Celles-ci ne doivent jamais être décrites comme des travaux effectués. Le Volume 03 est dédié à l'installation/deploiement et les volumes ultérieurs au N3 avancé, GitOps/Operators, HA/DR et tests en plateformes adaptées.

## Principales vérifications factuelles

1. **etcd / PRA :** la [documentation de restauration 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/backup_and_restore/control-plane-backup-and-restore) impose une sauvegarde prise à la même version z-stream pour le restore d'un état antérieur. L'archive associe snapshot et ressources static Pod.
2. **Machine API / autoscaler :** [la documentation 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/machine_management/applying-autoscaling) exige un MachineAutoscaler associé à des compute MachineSets pour que le ClusterAutoscaler puisse les augmenter. Les restrictions de `minReplicas: 0` dépendent du provider.
3. **OLM v1 :** [les release notes 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes) distinguent des fonctionnalités GA et Technology Preview. L'existence de la ressource ClusterExtension ne qualifie pas toutes les capacités comme GA.
4. **ClusterExtension :** [la référence d'API officielle](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/operatorhub_apis/clusterextension-olm-operatorframework-io-v1) confirme le modèle source/catalogue, version semver, channels et les risques de `SelfCertified`.
5. **CRD :** [la documentation Kubernetes](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/) impose la préservation de la plupart des métadonnées, l'ordre des objets dans ConversionReview et le traitement explicite de storedVersions. Le webhook de conversion n'est pas un validateur de sécurité métier.
6. **MCO :** aucun `maxUnavailable=1` universel n'est affirmé pour tous les pools; le lecteur doit consulter `spec.maxUnavailable` et les règles de sa topologie.
7. **OS workers RHEL :** divergence entre les [notes de version](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/release_notes/ocp-4-22-release-notes), les [guides d'architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture) et des procédures d'installation. Le [registre d'errata](ERRATA_V01_V02_20261011.md) demeure obligatoire.

## Revue des risques

- **PRA etcd :** aucune commande destructive dans les ateliers.
- **OLM / Machine API :** exemples non déployables, pas de création de Machine ni d'extension.
- **Confidentialité :** secrets et données du CRC jamais collectés durant cette publication.
- **Propriété intellectuelle :** schémas SVG originaux et descriptions rédigées sans copier les images officielles; les sources citées par liens. Les licences de redistribution demeurent distinctes du droit de consulter le dépôt public.
- **Mermaid :** 4 diagrammes SVG intégrés au PDF, les autres exemples Mermaid demeurent comme code lisible. Ce compromis est déclaré.
- **Défauts résiduels :** les contraintes de support exactes de chaque provider, z-stream et Operator tiers doivent être revérifiées pour une cible réelle. Cela ne bloque pas une **référence documentaire avec caveats**.

## Décision

**V02_CONTENT_CLOSED_DOCUMENTARY_SCOPE** une fois la CI de validation PDF 1.2 réussie. Ne pas considérer cette décision comme une homologation, une certification OpenShift ou un test HA/PRA.


## Publication vérifiée de l'édition 1.3

Le [contrôle de publication](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38217687784) est PASS (117 tests/125 liens). L'édition 1.2 présentait un défaut visuel de glossaire; une source Markdown corrigée, un test de régression et une vérification visuelle de la dernière page ont permis de publier [l'édition 1.3](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/tag/v02.3-20261012) sans écraser les éditions antérieures. **C7 : PASS.** La décision **V02_CONTENT_CLOSED_DOCUMENTARY_SCOPE** est effective. Aucune revendication runtime supplémentaire.
