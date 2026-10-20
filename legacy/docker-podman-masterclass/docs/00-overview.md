# Vue d’ensemble

## Docker vs Podman (en bref)
- Docker : daemon (dockerd), modèle “client/serveur”.
- Podman : daemonless, rootless-first, “pods” (similaire Kubernetes), compatible OCI.

## Objectif du repo
Te faire pratiquer les patterns indispensables :
- construire des images propres
- exécuter localement avec volumes/réseaux
- packager une stack via Compose
- livrer une image “prod-like” (non-root, multi-stage, healthcheck, read-only fs)
- maîtriser Podman rootless + pods
