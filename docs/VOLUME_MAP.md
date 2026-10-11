# Carte éditoriale — 12 volumes

**Édition de travail 2026–2030**. Les sous-chapitres sont des intentions de couverture et non des contenus déjà terminés. **Aucune pagination cible : chaque volume est évalué sur sa couverture, sa profondeur, ses preuves et son utilité.**

## V01 — Foundations
1. Pourquoi Kubernetes et OpenShift : positionnement, usages et limites.
2. Linux, processus, namespaces, cgroups, filesystem et réseau.
3. OCI, images, couches, signatures et registres.
4. Kubernetes : API, desired state, reconciliation, controllers, scheduler.
5. Pods, Deployments, Services, ConfigMaps, Secrets, volumes.
6. Différences OpenShift : RHCOS, CRI-O, SCC, Routes, Operators, Console et oc.
7. Premier lab en lecture seule; revue de conception et quiz.

## V02 — Platform Internals
1. Topologies de clusters, plans de contrôle et rôles des nœuds.
2. kube-apiserver, etcd, scheduler, controllers et admission.
3. OpenShift API, CVO, MCO, Machine API et cycle de configuration.
4. RHCOS, Ignition, CRI-O, kubelet et configuration système.
5. Operators, catalogues, lifecycle et gestion de version.
6. État du cluster, métriques internes et diagnostic control plane.
7. Architecture ADR : topologie et blast radius.

## V03 — Install & Operate
1. Préparatifs CPU, RAM, réseau, DNS, certificats et identity.
2. CRC et laboratoires sur poste contraint; limites de représentativité.
3. SNO, topologies compactes, multinœuds et haute disponibilité.
4. Bare metal, vSphere, IPI, UPI et Agent-based Installer.
5. Installations cloud managées, disconnected, mirrored registries.
6. Installation, vérification, accès et cycle de vie de la configuration.
7. Inventaire, backups préalables et day-1 runbooks.

## V04 — Networking
1. OSI/TCP-IP, CNI et modèle réseau Kubernetes.
2. OVN-Kubernetes et fonctionnement du dataplane.
3. Services, DNS, Routes, Ingress et certificats TLS.
4. NetworkPolicy, segmentation, egress et exposition.
5. Multus, secondary networks, load-balancing et architectures hybrides.
6. Inspection DNS, flux, latence et packet tracing.
7. Zero-trust network et modèles de frontières de confiance.

## V05 — Data & Storage
1. Stateless vs stateful et classes de stockage.
2. CSI, PV/PVC, StorageClass, access modes et expansion.
3. ODF/Ceph selon déploiement et prérequis.
4. StatefulSets, bases de données, cohérence et sauvegarde.
5. Snapshots, restore, RPO/RTO et DR tests.
6. Cryptage, rétention, migration et coûts.
7. Décisions d'architecture data sur OCP.

## V06 — Security & Compliance
1. Responsabilité partagée et threat modeling.
2. AuthN/AuthZ, OIDC, RBAC, service accounts et audit.
3. SCC, pod security, seccomp, capabilities et isolation.
4. Secrets, KMS, cert-manager, Vault, External Secrets.
5. NetworkPolicy, image policy, admission et signature.
6. Scanning, SBOM, ACS, conformité et evidence.
7. Cas banque/assurance, données sensibles, PCI/DORA selon applicabilité.

## V07 — DevSecOps & GitOps
1. Git workflows, déclaratif et supply chain.
2. Pipelines : source → test → build → registry → GitOps.
3. Helm, Kustomize, templates et overlays.
4. Argo CD : applications, sync, drift, self-heal, prune, rollback.
5. Promotion multi-environnements et stratégie secrets.
6. SBOM, vulnérabilités, signatures Cosign et politiques.
7. Contrôles de livraison, attestations et auditabilité.

## V08 — Kubernetes Operators
1. Operator pattern, CRD, CR, reconciliation et ownership.
2. Go, Kubebuilder, clients, informers et controller-runtime.
3. SSA, conditions, events et idempotence.
4. Reprises après erreurs, finalizers et deletion policies.
5. Tests envtest/Kind, métriques, leader election, RBAC.
6. OLM, catalogues, bundles et upgrades.
7. Scénarios Day-2 et dossier d'architecture Operator.

## V09 — SRE & Troubleshooting
1. SLI, SLO, erreurs, capacité et fiabilité.
2. Prometheus, metrics, alerting, OpenTelemetry et logs.
3. Baselines, benchmarks et analyse des ressources.
4. Triage des nœuds, Pods, control plane et workloads.
5. Incident N3 : symptômes → hypothèses → evidence → recovery.
6. Chaos/DR drill, rollback et postmortem.
7. Sizing, performance, astreinte et runbooks.

## V10 — HA, DR & Multicluster
1. Modes de panne, domaines de défaillance et blast radius.
2. HA infra, applicative et stockage.
3. Backup/restore et validation d'intégrité.
4. Upgrades, compatibility windows et version skew.
5. DR régional, DNS, données et RPO/RTO.
6. ACM, fleet governance et architectures multicluster.
7. Plans de migration, cutover et retour arrière.

## V11 — Platform Engineering
1. Produits plateforme, contrats et modèle de service.
2. Backstage, catalog, golden paths, self-service.
3. Platform API, quotas, isolation et tenancy.
4. CI/CD platform, sécurité, policy-as-code et IDP.
5. Sizing, FinOps, chargeback, showback.
6. Green IT : énergie, empreinte carbone, densité, mesure.
7. Roadmap de plateforme et modèle opérationnel.

## V12 — Advanced Architectures
1. RHOAI et architecture d'inférence/entraînement selon besoins.
2. GPU scheduling, isolation et MLOps sur clusters.
3. OpenShift Virtualization et coexistence VM/conteneurs.
4. Edge, gestion des flottes et disconnected.
5. EDA, IBM MQ, API management et architecture événementielle.
6. Cas bancaires et assurance : résilience et gouvernance.
7. Architecture hybrid/multicloud, tradeoffs et étude de cas complète.

## Interfaces entre volumes

- Le V01 fournit le vocabulaire commun; pas de duplication détaillée des internes V02.
- Le V06 fixe les exigences de sécurité réutilisées dans V04, V07, V08 et V12.
- Les labs GitOps D-091 alimentent V07 et V09; l'Operator D-093 alimente V08.
- D-100 alimente V06/V07/V10/V11 sous réserve des gates réellement démontrées.
- Les sujets IA infrastructure renvoient à la bible IA; le V12 traite les spécificités de déploiement **sur OpenShift**, sans refaire une bible générale IA.
