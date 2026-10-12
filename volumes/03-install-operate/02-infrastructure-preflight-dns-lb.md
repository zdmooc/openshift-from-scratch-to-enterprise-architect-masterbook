# 02 — Préflight Day-0 : DNS, load balancing, adresses, ports et PKI

**Volume 03 · DRAFT · OCP 4.22 · Préflight de lecture, aucun changement d'infrastructure.**

## 1. L'installation échoue souvent avant Kubernetes

Une installation OpenShift dépend d'un minimum de services d'infrastructure qui doivent exister avant la convergence du control plane : résolution DNS, adresses IP, connectivité, routes réseau, load balancers selon topologie, synchronisation temporelle et sources d'images.

Le caractère « automatisé » de l'IPI ne supprime pas le besoin de comprendre ces dépendances. Pour UPI, elles sont encore plus visibles parce que le client configure des éléments explicitement.

## 2. Noms DNS structurants

Pour le cluster fictif \`training\` sous le domaine \`example.invalid\`, les noms de référence sont :

| FQDN | Fonction pédagogique |
|---|---|
| \`api.training.example.invalid\` | Endpoint externe de l'API Kubernetes/OpenShift |
| \`api-int.training.example.invalid\` | Endpoint API interne selon architecture |
| \`*.apps.training.example.invalid\` | Wildcard des Routes et Ingress applicatifs |
| Noms des hosts | Résolution directe/inverse selon la méthode et les exigences de l'installateur |

Les noms \`.invalid\` sont expressément fictifs et ne désignent aucun cluster en service.

**Un A record DNS résolu n'est pas une preuve d'API saine.** La résolution doit être combinée avec l'état des LB/backends et les certificats.

### 2.1 DNS, ingress et contrôle de sécurité

Une configuration DNS correcte doit résoudre vers la ou les adresses de front attendues. Selon le provider, les endpoints API et les Routes peuvent être exposés de manière publique, privée ou mixte. La décision doit être guidée par la classification des flux : un endpoint accessible sur un réseau public ne devient pas sûr parce qu'il exige un token.

La wildcard \`*.apps\` doit respecter le nom de domaine autorisé et la gestion des certificats d'Ingress. Le DNS API et le DNS des applications peuvent suivre des cycles de vie distincts.

## 3. Frontières de load balancing

En architecture UPI classique, on distingue au moins :

| Flux | Rôle | Points d'attention |
|---|---|---|
| API Kubernetes | Connexions clients et contrôleurs vers kube-apiserver, couramment TCP 6443 | Health checks du backend, TLS et DNS |
| Machine Config Server | Services de bootstrap/configuration selon installation, couramment TCP 22623 | Périmètre d'accès interne adapté, séquence bootstrap |
| Ingress HTTP/HTTPS | Accès applicatif, généralement TCP 80/443 | Contrôleurs Ingress, Routes, certificats |
| etcd internode | Communication interne de consensus, ports dédiés selon architecture | Latence, confinement et certs; pas une exposition applicative |

Le fait que le guide mentionne un port ne signifie pas qu'il doit être ouvert sur Internet. Le plan de flux doit documenter **source, destination, protocole, port et justification**. Les responsabilités évoluent entre IPI, UPI, SNO, hosted control planes et providers spécifiques.

### 3.1 Chemin logique d'une requête API

~~~mermaid
flowchart LR
    ADMIN[Client oc autorisé] --> DNS[DNS api FQDN]
    DNS --> VIP[VIP ou Load Balancer API]
    VIP --> APIS[kube-apiserver disponibles]
    APIS --> ETCD[etcd quorum]
~~~

Une sonde TCP du LB est un indice de connectivité, non une preuve qu'etcd possède le quorum ou que l'API accepte une écriture.

## 4. Bootstrap : un intervalle de vie différent du runtime

L'installation peut utiliser un nœud bootstrap temporaire selon la méthode. Des services, endpoints et adresses sont nécessaires pendant la création de la plateforme, puis l'architecture cible change lorsque les composants de contrôle sont prêts.

**Erreur d'architecture :** supprimer trop tôt des routes ou LB destinés au bootstrap sans avoir une condition formelle de fin du bootstrap. Il faut disposer de la chronologie de convergence et de l'état des opérateurs avant de retirer les éléments éphémères.

De même, l'installateur ne doit pas être relancé sans comprendre si l'infrastructure existante est une création partielle ou un cluster en cours d'installation.

## 5. Accès Internet, proxy et disconnected

Trois modes doivent être distingués :
1. direct connected : accès aux registries/services requis et règles d'egress;
2. via proxy : certificats de confiance, exclusion noProxy, bootstrap et accès interne;
3. disconnected : images et catalogues nécessaires disponibles sur miroir privé, DNS/routage et PKI opérationnels.

Ne pas présumer que le proxy d'un poste administrateur suffit pour les nœuds. Les hôtes du control plane et les composants de cluster ont leurs propres chemins vers les sources d'images et APIs nécessaires.

## 6. Synchronisation du temps et PKI

Les certificats et tokens reposent notamment sur une horloge valide. Une dérive de temps peut provoquer des échecs TLS ou d'identité qui ressemblent à des incidents réseaux.

Avant installation, décrire :
- sources de synchronisation accessibles par les nœuds;
- stratégie DNS et autorité des certificats;
- nom des endpoints et SANs attendus;
- gestion des CAs internes dans les registries/proxies;
- rotation et procédure d'incident en cas de cert expiré.

On ne doit pas contourner un certificat non approuvé par \`--insecure-skip-tls-verify\` comme solution durable.

## 7. Préflight de lecture depuis une machine d'administration autorisée

Les commandes suivantes servent à vérifier la **résolution et la connectivité** sans modifier le cluster, et leurs FQDN doivent être remplacés par ceux du projet autorisé.

~~~bash
# Exemples pédagogiques de lecture ; les FQDN .invalid ne sont pas réels.
dig +short api.training.example.invalid
dig +short api-int.training.example.invalid
dig +short test.apps.training.example.invalid

# Uniquement dans un environnement de test et avec une cible valide :
# nc -vz api.training.example.invalid 6443
# openssl s_client -connect api.training.example.invalid:6443 \
#   -servername api.training.example.invalid -verify_return_error
~~~

Une commande \`dig\` vide sur \`.invalid\` est le résultat attendu ici, pas un incident. Les commandes TCP/TLS réelles demeurent commentées afin de ne pas scanner involontairement des systèmes extérieurs.

### 7.1 Critères de preuve

Un dossier de préflight doit comporter :
- date/fuseau, OCP cible et méthode/provider;
- source du contrôle (poste administrateur, réseau et DNS);
- FQDN anonymisés et adresses attendues;
- réponses DNS directes/inverses quand requises;
- accès port/api depuis les flux approuvés;
- enregistrement des droits et responsabilités LB;
- route vers registry/proxy ou miroir;
- matrice de certificats et source temporelle;
- écarts connus et décisions de go/no-go.

L'exécution d'un ping ne valide aucun de ces contrôles de manière exhaustive.

## 8. Tableau des incidents de bootstrap

| Symptôme | Hypothèses | Vérification discriminante |
|---|---|---|
| DNS api introuvable | Zone déléguée, enregistrement manquant, resolver inadapté | Query depuis le réseau d'installation |
| TCP 6443 inaccessible | LB/firewall/backends/API non prête | Route, backend, health |
| TLS SAN mismatch | Cert émis pour un autre FQDN | Nom SNI, certificat/CA |
| Pull d'image impossible | Registry, proxy/CA/credentials ou miroir incomplet | URL/digest et chemin de pull |
| Bootstrap ne termine pas | DNS, flux, machines, images, etcd et configurations | Chronologie des événements de l'installateur |
| Ingress indisponible | Routes/wildcard, ports 80/443, Pods ingress | DNS, LB et IngressControllers |
| Machine crée mais Node ne rejoint pas | Bootstrap RHCOS, réseau, kubelet, provider | Machine status et Node/events |

## 9. ADR de responsabilité : exemple fictif

**Contexte :** une équipe bancaire possède la plateforme OpenShift, tandis que DNS/LB sont exploités par une autre équipe réseau. Les redirections et firewalls traversent plusieurs zones de sécurité.

**Décision :** définir des propriétaires de FQDN, VIP, certificats, règles de flux et tests négatifs; archiver le préflight avant la fenêtre d'installation. Les changements aux LB et à la PKI utilisent des procédures de changement dédiées, indépendamment de l'installateur.

**Acceptation :** les flux depuis chaque réseau autorisé sont testés; les destinations sont conformes au schéma approuvé; aucune donnée sensible n'a été versée dans le dépôt public.

## 10. Questions d'architecte

1. Pourquoi tester DNS depuis le réseau bootstrap et pas uniquement depuis le poste admin ?
2. Que prouve un port TCP 6443 joignable ? Que ne prouve-t-il pas ?
3. Pourquoi ne pas publier 22623 sur Internet sans justification de support ?
4. Comment distinguer une erreur DNS d'une erreur SAN TLS ?
5. Pourquoi une installation disconnected nécessite-t-elle un accès à un registry miroir ?
6. Pourquoi la synchronisation temporelle est-elle un prérequis de sécurité ?
7. Quel signal permet de retirer l'infrastructure bootstrap temporaire ?

## Sources

- [Red Hat — Installation overview OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installation_overview/ocp-installation-overview)
- [Red Hat — Bare metal preparation OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_bare_metal/index)
- [Red Hat — User-provisioned infrastructure](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/installing_on_any_platform/installing-platform-agnostic)
- [Red Hat — Disconnected installation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/disconnected_environments/index)

**Aucune modification DNS, LB, certificat, cluster ou CRC n'a été effectuée pour ce chapitre.**
