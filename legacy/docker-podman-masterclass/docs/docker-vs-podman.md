# Docker vs Podman : différences à connaître

## Commandes équivalentes
- `docker build` ↔ `podman build`
- `docker run` ↔ `podman run`
- `docker ps` ↔ `podman ps`
- `docker logs` ↔ `podman logs`
- `docker exec` ↔ `podman exec`

## Points structurants
- Podman rootless : pas de daemon, meilleure posture de sécurité par défaut.
- Podman pods : `podman pod create`, `podman pod ps` (utile pour “penser Kubernetes”).
- Compose :
  - Docker : `docker compose ...`
  - Podman : `podman-compose ...` (ou équivalents selon environnement)

## Recommandation pratique
- Développer avec Docker **ou** Podman : OK.
- Pour une trajectoire Kubernetes/OpenShift : Podman apporte un “mindset” plus proche (pods, rootless, OCI).
