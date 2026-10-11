# Lab V02-L02 — Quorum et défaillances corrélées, simulation Python sans cluster

**Mode : OFFLINE_TEST · Aucune connexion à etcd ou OpenShift**

## Objectif

Découvrir la différence entre un nombre de membres votants et leur répartition physique. Le modèle ne traite que la majorité mathématique, pas les délais de réseau ni la disponibilité de disques ou de l'API.

## Exécution

~~~bash
python -m examples.v02.quorum_model examples/v02/cases/etcd-three-zones.json
python -m examples.v02.quorum_model examples/v02/cases/etcd-correlated-failure.json
python -m unittest discover -s tests -p 'test_*.py' -v
~~~

## Résultat attendu

- Trois membres A, B, C répartis en trois zones : si la zone C disparaît, A+B représentent deux votants et la majorité **peut** subsister.
- Trois membres mais deux membres dans un même rack : la perte de ce rack supprime deux membres, ne laisse que 1/3 et la majorité est **impossible**.

La réponse « majority_possible=true » ne signifie **jamais** qu'un cluster etcd réel dispose d'un leader, peut continuer à écrire ou a une latence acceptable.

## Tests négatifs

Le programme rejette les membres dupliqués, tailles invalides, noms de zones inconnus, schémas additionnels et types incorrects. Il ne dispose d'aucun mot de passe ni fonctionnalité de redémarrage, de modification du membership ou de restauration.

## Application à OpenShift

Avant d'affirmer que trois masters assurent la haute disponibilité, il faut vérifier la topologie réelle, les domaines de panne, les disques, les certificats, le LB et effectuer une validation sur un environnement autorisé.

**Ne pas pratiquer la perte de quorum sur un CRC ou un cluster partagé pour ce laboratoire.**
