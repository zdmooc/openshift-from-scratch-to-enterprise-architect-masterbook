# Roadmap 6 semaines (Docker + Podman)

## S1 — Images & runtime
- layers, cache, tags
- build/run/logs/exec
- nettoyage (images/containers)

## S2 — Volumes & réseaux
- bind mounts vs named volumes
- user permissions
- networks bridge + DNS interne

## S3 — Compose
- services, depends_on, env, healthchecks
- profiles (dev vs prod)
- override compose

## S4 — Image “prod-like”
- multi-stage
- non-root
- healthcheck
- read-only filesystem (quand possible)

## S5 — Podman avancé
- rootless (stockage, ports)
- pods
- podman machine (Windows/macOS)

## S6 — Registry & sécurité
- login/push/pull
- signatures/OCI (optionnel)
- scanning (outil au choix)
