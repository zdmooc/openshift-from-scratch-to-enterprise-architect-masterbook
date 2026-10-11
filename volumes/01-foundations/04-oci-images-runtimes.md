# 04 — OCI, images, registries et chaîne d'exécution

**Volume 01 · DRAFT · Niveau : développeur → architecte DevSecOps**  
**Référentiel : OCI Image, Runtime et Distribution Specifications ; OCP 4.22**  
**Preuve : PUBLIC_VERIFIED, procédures non exécutées lors de cette rédaction.**

## 1. Le contrat d'interopérabilité

OCI n'est pas un runtime, ni un produit d'orchestration, ni un registre. L'Open Container Initiative maintient trois spécifications complémentaires :

1. **Image Spec** — représentation d'une image et de ses composants.
2. **Distribution Spec** — protocole de distribution, découverte et gestion du contenu d'un registre.
3. **Runtime Spec** — comment un bundle de système de fichiers et sa configuration sont exécutés en tant que conteneur.

Ne pas confondre **format de l'image** et **mécanisme de démarrage**. Une image est un artefact; un conteneur est une instance de processus issue de cet artefact, avec un état éphémère.

## 2. Structure d'une image : index, manifest, configuration, layers

~~~mermaid
flowchart TB
  NAME[Nom et tag, ou référence digest] --> IDX[Image index éventuel]
  IDX --> AMD[Manifest plateforme amd64]
  IDX --> ARM[Manifest plateforme arm64]
  AMD --> CONF[Image config : entrypoint, env, user]
  AMD --> L1[Layer 1 : base]
  AMD --> L2[Layer 2 : dépendances]
  AMD --> L3[Layer 3 : application]
  ARM --> AC[Config + layers arm64]
~~~

L'index peut référencer des manifests distincts pour plusieurs architectures ou variantes. Un manifest contient des descripteurs de la configuration et des couches; un **digest** est un identifiant cryptographique du contenu. Les layers construisent un système de fichiers par superposition; un changement dans une couche peut modifier les digests des manifests qui la référencent.

### Exemple de structure logique simplifiée

**ILLUSTRATIVE_ONLY** : ce JSON est un exemple pédagogique, pas un manifest complet ni un document à pousser dans un registre.

~~~json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:<digest-reel-config>",
    "size": 1234
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:<digest-reel-layer>",
      "size": 5678
    }
  ]
}
~~~

Les chaînes entre chevrons sont des placeholders. Un véritable manifest doit référencer des blobs existants avec leurs tailles et digests exacts.

## 3. Tags, digests et provenance

Un tag tel que `application:stable` est un nom pratique, mais il est **mutable** si la politique du registre l'autorise. Une référence par digest, `registry.example.org/app@sha256:...`, identifie précisément un manifest (ou index). Cela améliore la reproductibilité, mais **n'établit pas à lui seul que l'image est sûre ou approuvée**.

Chaîne d'approvisionnement recommandée :

~~~mermaid
flowchart LR
  SRC[Source revue] --> BUILD[Build contrôlé]
  BUILD --> TEST[Tests et analyse]
  TEST --> SBOM[SBOM / provenance]
  SBOM --> SIGN[Signature / attestation]
  SIGN --> REG[Registry]
  REG --> POL[Politique de déploiement]
  POL --> NODE[CRI-O / nœud]
~~~

Il faut distinguer plusieurs propriétés indépendantes :

- **Intégrité** : le contenu reçu est-il celui identifié par son digest ?
- **Authenticité** : qui a publié/signé cet artefact et avec quelle identité ?
- **Provenance** : quelle source et quel pipeline l'ont produit ?
- **Vulnérabilités** : quels composants sont connus comme vulnérables, à la date du scan ?
- **Autorisation** : ce composant est-il autorisé dans cet environnement ?

Un scan réussi ne prouve pas l'absence de défauts, et une signature valide ne prouve pas qu'un build est sain : elle doit être rapprochée d'une identité et d'une politique de confiance.

## 4. Ce que font les composants sur un nœud

Le kubelet pilote la vie des Pods; l'interface **CRI** lui permet de communiquer avec un runtime de haut niveau tel que CRI-O. Ce dernier gère l'exécution des conteneurs à travers un runtime OCI bas niveau, et interagit avec le stockage d'images et le réseau.

~~~text
PodSpec dans l'API
      │
      ▼
kubelet (agent de nœud)
      │ CRI
      ▼
CRI-O  ─────→ téléchargement et gestion des images
      │
      ▼
runtime OCI (crun / runc selon version/configuration)
      │
      ▼
namespaces + cgroups + SELinux/seccomp
      │
      ▼
processus applicatif
~~~

**Idée importante pour l'entretien** : Docker est un ensemble d'outils/concepts historiques; Docker Engine n'est pas le moteur des conteneurs OCP 4.22. Cela n'interdit pas la construction d'images compatibles par différents builders. Le contrat pertinent est le format et la compatibilité de la chaîne.

## 5. Anatomie d'un échec d'image

| Étape | Exemple de symptôme | Observation utile |
|---|---|---|
| Résolution référence | Nom de tag erroné | Image déclarée, référence et registre |
| Authentification | ImagePullBackOff/ErrImagePull | Events, pull secret, accès registre |
| Téléchargement | Échec réseau/CA | DNS, proxy, autorité de certification, egress |
| Architecture CPU | Format exécutable invalide | Plateforme image et architecture des nœuds |
| Démarrage | CrashLoopBackOff | Commande, variables, sorties et healthchecks |
| UID/GID | Permission denied | SCC, propriétaires, chemins d'écriture |
| Init longue | Readiness jamais Ready | Startup/readiness probes et dépendances |

Des états Kubernetes comme ImagePullBackOff doivent être diagnostiqués par les Events et le PodSpec; la cause peut être l'authentification, la DNS, la politique egress, le proxy, le CA ou la référence, pas seulement l'absence de l'image.

## 6. Préparer une image compatible OpenShift

Une application portable doit éviter d'exiger root, un UID fixe arbitraire ou l'écriture dans des répertoires système non autorisés. Sur OpenShift, certaines SCC peuvent affecter un UID dans une plage; l'image doit fonctionner avec cet UID et disposer d'un chemin d'écriture conforme à sa politique.

Patron de construction **conceptuel** (à adapter selon le langage et la base image autorisés) :

~~~Dockerfile
# PSEUDO-EXEMPLE : remplacer par une image de base approuvée et figée par digest.
FROM registry.example.invalid/approved/runtime@sha256:<digest>
WORKDIR /opt/app
COPY --chown=0:0 ./app/ /opt/app/
# Sur de nombreuses images conçues pour OpenShift, les fichiers
# nécessaires doivent être accessibles à un UID non-root arbitraire.
# Les permissions précises sont à établir pendant le build.
EXPOSE 8080
ENTRYPOINT ["/opt/app/server"]
~~~

Ce Containerfile n'est **pas exécutable tel quel** : registry.example.invalid et le digest sont volontairement invalides. Ne pas copier des instructions permissives comme chmod 777 sur les données. Le schéma de permissions doit assurer la séparation entre répertoires en lecture seule, volumes de données, répertoires temporaires et exécution.

Pour une application web, viser en général un port non privilégié (par exemple 8080) et documenter les permissions d'écriture réelles nécessaires. Il faut analyser les capacités requises par l'application plutôt que supposer une image universellement compatible.

## 7. Multi-architecture et portabilité

L'existence d'un image index multi-architecture ne garantit pas que toutes les plateformes ont été publiées, que les extensions natives sont compatibles, ou que les performances sont identiques. Avant une migration x86_64 → ARM64 :

1. Inventorier les images et les dépendances binaires.
2. Vérifier les manifests et les architectures publiées.
3. Rebuilder/tester les extensions natives.
4. Exécuter des tests fonctionnels et de performance sur la cible.
5. Vérifier la compatibilité de la plateforme OpenShift et des Operators.
6. Mettre à jour l'architecture et la politique de supply chain.

## 8. Laboratoire d'inspection (local, sans accès cluster)

Pré-requis : Podman ou Skopeo déjà installés. Ces commandes sont de lecture de métadonnées ou de registre, mais peuvent contacter le réseau. **Ne pas utiliser d'identifiants de registre dans la ligne de commande**.

~~~bash
# Inspection des images locales avec Podman
podman images --digests

# Sur une image déjà présente localement, sans téléchargement :
podman image inspect IMAGE_LOCALE

# Si un registre externe est explicitement autorisé :
skopeo inspect docker://REGISTRY/IMAGE:TAG
skopeo inspect --raw docker://REGISTRY/IMAGE:TAG
~~~

Remplacer `IMAGE_LOCALE`, `REGISTRY` et `TAG` par des valeurs légitimes. L'option --raw montre typiquement un manifest ou un index; les champs changent selon média-type. Sur un poste Windows Git Bash, un moteur Podman doit être installé/configuré pour les commandes locales.

## 9. Questions d'architecture

1. **Un tag stable garantit-il un déploiement identique ?** Non, sauf politique d'immuabilité vérifiée; préférer le pin par digest pour un artefact exact.
2. **Un digest suffit-il à authentifier l'éditeur ?** Non : il atteste du contenu référencé, pas de l'identité de son producteur.
3. **Pourquoi séparer builder et runtime ?** Contrôler la surface d'attaque, la reproductibilité, le cycle de patching et les permissions.
4. **Peut-on déployer toute image Docker sur OpenShift sans modification ?** Le format peut être compatible, mais l'UID, les capacités, les réseaux, les volumes, les policies et l'architecture CPU peuvent empêcher une exécution correcte.
5. **Quelle est la différence OCI/CRI ?** OCI définit notamment les formats et l'exécution; CRI est le contrat kubelet ↔ runtime de conteneur.

## Références

- [OCI — overview](https://opencontainers.org/)
- [OCI — Image Specification](https://specs.opencontainers.org/image-spec/)
- [OCI — Runtime Specification](https://specs.opencontainers.org/runtime-spec/)
- [OCI — Distribution Specification](https://specs.opencontainers.org/distribution-spec/)
- [Red Hat — architecture OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)

**À compléter ultérieurement :** tests de signature et de SBOM en sandbox isolée, matrice de compatibilité des images, évaluation des outils de scan/policy (V07).
