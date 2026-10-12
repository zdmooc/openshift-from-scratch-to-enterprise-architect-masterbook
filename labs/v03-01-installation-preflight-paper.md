# V03-L01 — Dossier de préflight d'une installation OpenShift

**Mode : PAPER_LAB · DOCUMENTED_NOT_RUN · Aucune modification de DNS/LB, réseau, Machine ou cluster.**

## Contexte fictif

Une organisation veut installer OpenShift 4.22 sur bare metal en environnement hybride. La partie DNS/LB est opérée par l'équipe Réseau, les machines par l'équipe Infrastructure, la PKI par la sécurité et OpenShift par Platform Engineering.

## Travail demandé

Compléter la matrice suivante avant tout chantier réel :

| Gate | Information requise | Responsable | Résultat |
|---|---|---|---|
| P01 | Méthode supportée (IPI, UPI, Assisted, Agent-based) | Architecture/plateforme | À instruire |
| P02 | Nombre de nodes, rôles et domaines de panne | Infrastructure | À instruire |
| P03 | Ressources et réserves CPU/RAM/disque | Plateforme/Infra | À instruire |
| P04 | FQDN API externe/interne, wildcard apps | DNS | À instruire |
| P05 | LB API 6443 et backends | Réseau | À instruire |
| P06 | Machine Config Server 22623 si requis | Réseau/plateforme | À instruire |
| P07 | Ingress 80/443 et certificats | Réseau/PKI | À instruire |
| P08 | Accès registry, proxy/mirror, CA | Sécurité/Infra | À instruire |
| P09 | Synchronisation horaire et NTP | Infrastructure | À instruire |
| P10 | Compte provider, droits, quotas et support | Cloud/Infra | À instruire |
| P11 | Driver CSI et données applicatives | Stockage | À instruire |
| P12 | Procédure de reprise et support | Exploitation/N3 | À instruire |

Ne pas renseigner PASS sans observation datée correspondant à la plateforme et à la version cible.

## Exercices corrigés

**E1 :** Le FQDN API résout depuis le LAN admin, pas depuis le VLAN bootstrap. Résultat : préflight non conforme; requêtes DNS depuis chaque domaine réseau concerné et correction par le propriétaire.

**E2 :** TCP 6443 répond, mais les clients rejettent TLS. Résultat : LB joignable, mais nom, SAN, CA ou horloge à contrôler ; ne pas désactiver la vérification TLS.

**E3 :** Une infrastructure dite disconnected n'a pas de miroir de release. Résultat : pas de chemin fiable de pull d'images; installer bloqué ou fragile. Planifier un registry et une procédure de mirroring conforme.

**E4 :** Trois masters existent sur le même hyperviseur. Résultat : majorité etcd de trois membres possible mais pas de preuve de trois domaines de panne. Mettre à jour l'architecture physique et les attentes HA.

## Livrable pédagogique

Un dossier de décision de lancement **GO/NO-GO**, comprenant les preuves P01–P12, les risques résiduels, le plan de responsabilité et les dépendances externes. Le dossier est fictif tant qu'il n'est pas rempli sur un environnement réellement autorisé.

Sources : [OCP 4.22 Installation overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installation_overview/ocp-installation-overview).
