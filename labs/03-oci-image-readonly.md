# Lab V01-L03 — Inspection OCI et analyse de provenance

**Statut : DOCUMENTED_NOT_RUN · READ_ONLY**

## Objectifs

Distinguer manifest, index, layers et config; identifier digest et plateforme cible; vérifier si la chaîne d'approvisionnement expose provenance/SBOM/signature **sans supposer leur présence**.

## Chemin A : environnement avec Podman et image locale

~~~bash
podman images --digests
podman image inspect NOM_IMAGE_LOCALE
~~~

Remplacer le nom par une image réellement présente. Ne pas construire ni tirer d'image pour ce lab sauf autorisation explicite. Pour explorer le manifest sans image locale, Skopeo peut contacter un registry approuvé.

## Chemin B : registre autorisé

~~~bash
skopeo inspect --raw docker://REGISTRY/REPOSITORY:TAG
skopeo inspect docker://REGISTRY/REPOSITORY:TAG
~~~

Ce chemin **lit** des métadonnées, peut provoquer un accès réseau et nécessite parfois des identifiants. Une erreur d'authentification n'est pas une preuve que l'image n'existe pas.

## Analyse à produire

| Contrôle | Question | Preuve exigée |
|---|---|---|
| Image/media type | Manifest unique ou index ? | Champ mediaType |
| Intégrité | Digest réel observé ? | Valeur digest et contexte |
| Architecture | amd64/arm64 publiés ? | Descripteurs ou inspection |
| Configuration | User, entrypoint, env pertinents ? | Image config si accessible |
| Provenance | Qui a construit l'image ? | Attestation et identité vérifiées, sinon UNKNOWN |
| Sécurité | Vulnérabilités analysées ? | Rapport daté, sinon NOT_ASSESSED |
| Publication | Peut-on déployer ? | Décision conditionnelle, jamais « oui » par défaut |

## Limites

L'inspection d'un manifest ne suffit pas à obtenir les garanties de runtime, de signature, de sécurité applicative, ni de support vendeur. Aucun outil n'a été exécuté lors de la rédaction de ce laboratoire.
