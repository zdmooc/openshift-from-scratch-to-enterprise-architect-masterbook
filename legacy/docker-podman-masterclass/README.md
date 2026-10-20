# docker-podman-complete-masterclass

Référentiel “de bout en bout” pour maîtriser **Docker ET Podman** (avec des labs reproductibles) :
- Build & run (Dockerfile / Containerfile)
- Volumes / réseaux / logs
- Compose (docker compose) et alternatives Podman (podman-compose)
- Images propres (multi-stage, non-root, healthcheck)
- Rootless Podman + Pods
- Build avancé (buildx / buildah), registry, push/pull
- Sécurité (capabilities, read-only fs, user, secrets)

> Philosophie : *un même lab fonctionne* avec `ENGINE=docker` ou `ENGINE=podman`.

## Prérequis (au choix)
- Docker Desktop (Windows) **ou**
- Podman Desktop / Podman (Windows via WSL2 ou Podman machine)
- Git Bash (OK)

Vérifier :
```bash
docker version 2>/dev/null || true
podman version 2>/dev/null || true
```

## Démarrage rapide

### 1) Choisir un moteur (docker ou podman)
```bash
export ENGINE=docker   # ou podman
```

### 2) Lancer un premier lab
```bash
make lab01
make lab02
```

## Structure
- `docs/` : cours + différences Docker/Podman + runbooks
- `labs/` : labs pas-à-pas (commandes + expected output)
- `examples/` : mini-apps + Dockerfile/Containerfile
- `compose/` : stacks Compose prêtes à l’emploi
- `scripts/` : wrappers cross-engine (docker/podman)

## Convention
- `Dockerfile` : compatible Docker
- `Containerfile` : compatible Podman (souvent identique)
- Scripts : `scripts/engine.sh` choisit l’outil selon `ENGINE`.
