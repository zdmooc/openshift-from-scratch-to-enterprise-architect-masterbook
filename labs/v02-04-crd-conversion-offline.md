# V02-L04 — Évolution de CRD v1alpha1 → v1beta1 et ConversionReview

**Mode : OFFLINE_TEST · 20 tests Python · Aucun serveur webhook, aucune CRD déployée.**

## Objectif réel

Étudier une migration de schéma **avec perte d'information interdite**, distinguer \`served\`, \`storage\` et \`status.storedVersions\`, et comprendre pourquoi un webhook de conversion est un composant critique de disponibilité de l'API.

L'exercice concerne une API fictive \`CapabilityProfile\` :
- v1alpha1 : \`spec.enabled\` booléen;
- v1beta1 : \`spec.profile\` dans l'enum \`standard|disabled\`;
- \`spec.retentionDays\` conservé, entier de 1 à 365;
- les métadonnées \`uid\`, \`name\`, \`namespace\`, labels, annotations et \`status\` sont conservés à l'identique.

Aucune option \`enhanced\` n'est supportée tant qu'elle n'est pas convertible sans perte : l'exemple choisit de **refuser** ce cas plutôt que de supprimer une information.

## Fichiers livrés

- [CRD à deux versions — NON DÉPLOYABLE](../examples/v02/crd-versioning/crd-example-not-deployable.json) : l'URL du service de conversion est un placeholder inexistant.
- [Ressource alpha](../examples/v02/crd-versioning/alpha.json).
- [Ressource beta](../examples/v02/crd-versioning/beta.json).
- [ConversionReview fictive](../examples/v02/crd-versioning/review.json).
- [Modèle pur Python](../examples/v02/crd_versioning.py).
- [Tests unitaires](../tests/test_v02_crd_versioning.py).

## Exécution locale depuis la racine du dépôt

~~~bash
python -m examples.v02.crd_versioning examples/v02/crd-versioning/review.json
python -m unittest discover -s tests -p 'test_v02_crd_versioning.py' -v
~~~

La sortie contient \`response.uid\`, \`result.status=Success\` et \`convertedObjects\` à la version demandée. Les tests démontrent le round trip, les exclusions d'états non représentables, la préservation des métadonnées et status, l'ordre d'un batch, et le rejet des schémas invalides.

## Cas pratique : migration du stockage

1. Déployer et qualifier le service de conversion sur un environnement **d'essai autorisé**, avec TLS/CA corrects.
2. Servir simultanément les deux versions pour laisser migrer les clients.
3. Définir v1beta1 comme storage après validation.
4. Mettre en œuvre une migration des objets **déjà stockés**, car changer le storage seul ne les réécrit pas automatiquement.
5. Vérifier les anciennes valeurs dans \`status.storedVersions\`.
6. Retirer v1alpha1 du service uniquement après avoir migré les clients et les objets et après décision de version.
7. Documenter rollback de l'Operator et disponibilité du webhook sans chercher à downgrader OpenShift.

Ne pas retirer une ancienne version simplement parce que le nouveau controller est Running.

## Limite de preuve

Le modèle Python **n'implémente pas** un serveur HTTP/TLS, les vérifications d'identité du kube-apiserver, les conditions SSA, la validation OpenAPI du serveur, la StorageVersionMigration ni le comportement réel d'un webhook pendant un upgrade. Un résultat de test OFFLINE_PASS ne prouve pas une admission Kubernetes réussie.

## Sources

- [Kubernetes — Versions de CRDs](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/)
- [Kubernetes — CRD validation](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/)


## Point de vigilance : ne jamais confondre validation et conversion

L'enum \`standard|disabled\` **n'admet pas** une valeur \`enhanced\` dans cette version de schema. L'application doit refuser les valeurs invalides au niveau de la validation de l'API. Le module Python les refuse à titre de **défense dans une simulation**, pas comme règle de fonctionnement d'un webhook Kubernetes de production. Un vrai webhook de conversion doit pouvoir traiter **toutes les ressources qui ont été admises par les anciennes versions**; sa défaillance peut bloquer l'accès à ces ressources.

La documentation Kubernetes déconseille expressément d'utiliser un webhook de conversion comme mécanisme principal de validation. Toute future extension du profil nécessite une stratégie de conversion totale ou une restriction des clients avant que de nouvelles valeurs ne soient persistées.

[Source Kubernetes — Conversion webhooks, failure consequences and permissible mutations](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definition-versioning/).
