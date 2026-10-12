# Volume 02 — validation du contenu

**12 octobre 2026 · Statut : CLOSED_DOCUMENTARY_SCOPE.** Le contenu est la mesure de complétude; la pagination et les comptes de tests ne sont pas des objectifs.

| Gate | Résultat | Limites assumées |
|---|---|---|
| C1 — Couverture | PASS : 12 chapitres sur API/etcd, scheduler, Operators/CVO, MCO/RHCOS, CRI-O, admission, CRDs, Machine API, OLM et N3 | Installation réelle traitée dans V03 |
| C2 — Profondeur technique | PASS : mécanismes, états, alternatives, erreurs, preuves et cas bancaires | Aucun prétendu SLO réel |
| C3 — Sources officielles | PASS_WITH_CAVEAT : versions et restrictions OCP 4.22 revues | Divergence documentaire RHEL workers signalée |
| C4 — Exemples et ateliers | PASS_DOCUMENTARY : 6 labs avec limites | 3 labs offline, exercices papier/read-only non exécutés |
| C5 — Honnêteté des preuves | PASS : OFFLINE_TEST, DOCUMENTED_NOT_RUN, REFERENCE_ARCHITECTURE distincts | Pas de runtime DR/HA/OLM/Machine API |
| C6 — Droits et sécurité | PASS_PUBLICATION_WITH_RESERVED_RIGHTS | Modèle de licences ouvertes mixtes à déterminer séparément |
| C7 — Mise en page et publication | PASS : PDF 1.3, sections extraites, liens contrôlés, dernière page inspectée | Schémas Mermaid non convertis tous en graphiques |

## Vérification de la release

- [CI édition 1.3 : SUCCESS](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/actions/runs/38217687784) — 117 tests automatisés, 125 liens Markdown et PDF complet.
- [Fichier PDF publié](https://github.com/zdmooc/openshift-from-scratch-to-enterprise-architect-masterbook/releases/download/v02.3-20261012/OpenShift_Masterbook_Volume_02_Edition_1_3_Zidane_Djamal_2026.pdf) — 12 chapitres, 6 laboratoires, étude bancaire, avis au lecteur, erratum, glossaire.
- [Rapport d'audit](V02_TECHNICAL_AUDIT_20261012.md).
- [Contrôle PDF](V02_RELEASE_VERIFICATION_1_3.md).

Les labs ne fournissent aucun accès au cluster et aucune preuve de conformité ou de capacité en production. Les licences futures et les nouvelles versions d'OpenShift feront l'objet de vérifications distinctes.

## Décision

**Volume 02 clos dans son périmètre documentaire le 12 octobre 2026.** La suite éditoriale est le [Volume 03](../volumes/03-install-operate/README.md) : installation, DNS, load balancers, topologies et premières opérations Day-1.
