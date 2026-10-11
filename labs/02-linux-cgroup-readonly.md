# Lab V01-L02 — Observation Linux des namespaces et des cgroups

**Statut : DOCUMENTED_NOT_RUN · READ_ONLY · Contexte : hôte Linux local ou VM Linux dédiée**

## Prérequis et sécurité

Cet atelier ne doit pas être exécuté sur un nœud OpenShift via une session privilégiée. Utiliser une VM Linux locale, WSL2 Linux ou un hôte Linux sur lequel vous possédez des droits légitimes. Git Bash sous Windows sans environnement Linux n'expose pas les mêmes chemins procfs/cgroup. Les résultats dépendent du noyau, de systemd et de la hiérarchie cgroup.

## Observation 1 : système et PID 1

~~~bash
uname -a
cat /proc/1/comm
id
ps -o pid,ppid,comm -p 1,$$
~~~

**Attendu :** identifier le noyau, l'init du contexte courant et le couple UID/GID. Si la session tourne dans WSL/VM/container, le contexte n'est pas celui d'un nœud OCP.

## Observation 2 : espaces de noms

~~~bash
ls -l /proc/self/ns
ls -l /proc/1/ns
cat /proc/self/cgroup
~~~

**Attendu :** des liens `net:[...]`, `pid:[...]`, etc. Leurs identifiants permettent une comparaison dans le **même noyau**, pas une comparaison entre machines. Une lecture peut être refusée pour des raisons de permissions.

## Observation 3 : cgroup v2

~~~bash
if test -e /sys/fs/cgroup/cgroup.controllers; then
  cat /sys/fs/cgroup/cgroup.controllers
  cat /proc/self/cgroup
  test -r /sys/fs/cgroup/cpu.stat && cat /sys/fs/cgroup/cpu.stat
  test -r /sys/fs/cgroup/memory.events && cat /sys/fs/cgroup/memory.events
else
  echo "cgroup v2 unifié non visible ici"
fi
~~~

Ne pas modifier `cpu.max`, `memory.max` ou la hiérarchie; l'objectif est de relier les concepts aux mécanismes. La racine cgroup visible peut être déléguée ou différente de la cgroup effective du processus.

## Diagnostic demandé

1. Identifier trois namespaces et expliquer leur effet.
2. Dire si la hiérarchie cgroup v2 est visible.
3. Expliquer pourquoi un quota CPU n'équivaut pas à une réservation de CPU.
4. Expliquer deux origines possibles de Permission denied autres que les bits rwx.

## Preuve minimale

Version noyau, contexte hôte/VM/WSL, fichier observé, date, permissions, absence de secrets, limites. **Aucune preuve n'a été produite pendant la rédaction de cette fiche.**
