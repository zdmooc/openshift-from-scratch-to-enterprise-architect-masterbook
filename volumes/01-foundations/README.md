# Volume 01 — Foundations

**État : 8 chapitres DRAFT et 7 laboratoires documentés, pas encore un volume FINAL.**  
**Périmètre : Linux → OCI → Kubernetes → OpenShift 4.22 → revue d'architecture.**

## Contenu technique

1. [Pourquoi OpenShift ?](01-what-is-openshift.md) : problématique d'orchestration et valeur de plateforme.
2. [Desired state et réconciliation](02-desired-state-and-operators.md) : controllers, Operators, Conditions et convergences.
3. [Linux : namespaces, cgroups et sécurité](03-linux-namespaces-cgroups.md) : PID/network/mount, quotas CPU/mémoire, SELinux/seccomp.
4. [OCI : images, runtimes et provenance](04-oci-images-runtimes.md) : manifest, index, tags/digests, signatures et distribution.
5. [Kubernetes API et workloads](05-kubernetes-api-workloads.md) : API, Deployment, Service, EndpointSlice, scheduling, probes, N3.
6. [OpenShift et capacités d'entreprise](06-openshift-enterprise-primitives.md) : RHCOS, MCO, CVO/OLM, Routes, RBAC/SCC.
7. [Évaluation et soutenance](07-review-and-evaluation.md) : 25 questions corrigées, 5 scénarios, grille de revue.
8. [Admission SCC/PSA, Routes TLS et NetworkPolicy](08-security-admission-routes.md) : séparation des contrôles, flux et erreurs d'admission.

[Glossaire du Volume 01](GLOSSARY.md)

## Labs documentés

- [L01 — Observation du cluster en lecture seule](../../labs/01-cluster-read-only.md).
- [L02 — Observer namespaces/cgroups Linux](../../labs/02-linux-cgroup-readonly.md).
- [L03 — Inspecter des images OCI](../../labs/03-oci-image-readonly.md).
- [L04 — Observer API, Pods, Services et EndpointSlices](../../labs/04-kubernetes-api-triage-readonly.md).
- [L05 — Revue d'architecture bancaire](../../labs/05-architecture-review-payments.md) (paper lab).

## Étude de cas complète : API bancaire

- [C01 — Architecture de référence](../../case-studies/v01-banking-api/01-reference-architecture.md)
- [C02 — Diagnostic N3 et preuves](../../case-studies/v01-banking-api/02-n3-triage-and-evidence.md)
- [C03 — ADR et dimensionnement argumenté](../../case-studies/v01-banking-api/03-adr-and-sizing.md)

## Validation et progression

Lire [docs/V01_PROGRESS.md](../../docs/V01_PROGRESS.md) pour la couverture effective, les lacunes et les prochains objectifs. Les fichiers portent des statuts **DRAFT / DOCUMENTED_NOT_RUN** ; le texte ne vaut pas preuve de lab.

Les critères de passage à FINAL restent ceux du [standard éditorial](../../docs/EDITORIAL_STANDARD.md). Aucun nouveau workload CRC n'a été exécuté pendant la rédaction.
