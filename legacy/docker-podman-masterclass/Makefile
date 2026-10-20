ENGINE ?= docker
COMPOSE ?= auto

.PHONY: info lab01 lab02 lab03 lab04 lab05 lab06 lab07 lab08 lab09 lab10 clean

info:
	ENGINE=$(ENGINE) ./scripts/info.sh

lab01:
	ENGINE=$(ENGINE) ./labs/lab01-build-run.sh

lab02:
	ENGINE=$(ENGINE) ./labs/lab02-volumes.sh

lab03:
	ENGINE=$(ENGINE) ./labs/lab03-networks.sh

lab04:
	ENGINE=$(ENGINE) ./labs/lab04-compose-stack.sh

lab05:
	ENGINE=$(ENGINE) ./labs/lab05-multistage.sh

lab06:
	ENGINE=$(ENGINE) ./labs/lab06-rootless-podman.sh

lab07:
	ENGINE=$(ENGINE) ./labs/lab07-pods-podman.sh

lab08:
	ENGINE=$(ENGINE) ./labs/lab08-registry.sh

lab09:
	ENGINE=$(ENGINE) ./labs/lab09-security-basics.sh

lab10:
	ENGINE=$(ENGINE) ./labs/lab10-debugging.sh

clean:
	ENGINE=$(ENGINE) ./scripts/cleanup.sh
