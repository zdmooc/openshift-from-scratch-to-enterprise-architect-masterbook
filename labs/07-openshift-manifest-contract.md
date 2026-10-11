# L07 — Contrat de manifests OpenShift contrôlé hors cluster

**Mode : OFFLINE_CONTRACT_TEST · Statut : LAB_DOC_PUBLISHED · Pas de runtime Kubernetes**

## Objectif

Comprendre les liens entre Namespace, ServiceAccount, Deployment, Service, Route et NetworkPolicy, puis empêcher la publication d'erreurs simples par des tests automatiques.

## Artefacts

Les six ressources JSON (format de données accepté par l'API Kubernetes) résident dans [examples/v01/manifest-contract](../examples/v01/manifest-contract/02-deployment.json). Le [validateur Python](../examples/v01/manifest_contract.py) et les [tests unitaires](../tests/test_manifest_contract.py) reposent sur la bibliothèque standard.

Ce bundle est **volontairement non déployable** :
- image \`registry.example.invalid\` avec digest fictif;
- host Route \`training.example.invalid\`;
- NetworkPolicy default-deny qui interdit ingress **et** egress;
- application et endpoints /ready et /health non fournis.

Il n'est pas recommandé de le déployer, ni sur CRC ni en production.

## Exécution (PC local, sans cluster)

~~~bash
python -m examples.v01.manifest_contract
python -m unittest discover -s tests -p "test_*.py" -v
~~~

Le validateur contrôle l'identité des ressources, les namespace/labels/selectors, Service ↔ port Pod, Route ↔ Service, cohérence du ServiceAccount, absence d'auto-montage de token, non-root, seccomp RuntimeDefault, absence d'élévation de privilège, capabilities drop ALL, ressources CPU/RAM et règles de default-deny.

### Exercices négatifs (sans cluster)

1. Changer \`Service.spec.selector.app.kubernetes.io/name\` en \`another\` : le test structurel doit refuser le bundle.
2. Mettre \`allowPrivilegeEscalation=true\` : le vérificateur doit échouer.
3. Changer Route \`termination\` en \`reencrypt\` sans modifier le contrat : le vérificateur doit échouer.
4. Ajouter une règle \`egress\` à NetworkPolicy : le contrat pédagogique de blocage doit échouer.
5. Remplacer le host .invalid par un vrai domaine : le validateur doit refuser ce qui pourrait être confondu avec un environnement réel.

Les tests négatifs démontrent **un contrat offline**, sans produire ni secret ni trafic réseau.

## Passage éventuel à un véritable déploiement

Requiert un nouveau dossier de validation avec :
- image signée/contrôlée et exécutable non-root, digest authentique et arch/OS compatibles;
- endpoint readiness/liveness effectivement implémentés;
- DNS/certificats et terminaisons TLS propres à la cible;
- NetworkPolicies autorisant explicitement DNS, ingress, observabilité, services nécessaires;
- quota du namespace, politiques SCC et PSA et droits RBAC;
- test \`oc apply --dry-run=server\` pour l'admission **avant** toute création réelle, avec autorisation de contact cluster;
- budget ressources, protocole de preuve, plan de nettoyage et rollback.

Même \`--dry-run=server\` contacte l'API, soumet une requête d'admission et peut engager des webhooks ; il ne doit pas être assimilé à un contrôle purement local et nécessite autorisation.

## Limite épistémique

Une réponse PASS du validateur ne garantit ni syntaxe admise par une version donnée d'OpenShift, ni bon placement, ni acceptation de SCC, ni absence de CVE, ni disponibilité métier. Le valideur ne lit aucun cluster.
