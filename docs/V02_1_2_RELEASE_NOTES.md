# Volume 02 — Édition documentaire 1.2

**Date : 12 octobre 2026 · Auteur : Zidane Djamal · Produit : OpenShift Container Platform 4.22 / Kubernetes 1.35.**

## Contenu inclus

- 12 chapitres : API, etcd, scheduler, CVO, MCO, kubelet/CRI-O, admission SCC/PSA, CRD, control plane HA, N3, Machine API, OLM Classic/v1.
- 6 ateliers : lecture seule, calcul de quorum, filtre scheduler, conversion CRD, autoscaling Machine API et choix OLM.
- 1 étude d'architecture bancaire, un glossaire, 4 schémas SVG et des illustrations Mermaid sous forme source lorsque non rendues.
- Avis au lecteur et erratum de support RHCOS/RHEL inclus directement dans le PDF.

## Corrections depuis l'édition 1.1

Relecture de la documentation officielle 4.22; ajout des chapitres Machine API et OLM, de la version de CRD convertible et de cas N3; explication du statut Technology Preview de fonctionnalités OLM v1, des restrictions provider pour MachineAutoscaler, de la compatibilité etcd restore z-stream et du contrat de ConversionReview; correction de l'affirmation trop générale sur maxUnavailable.

## Domaine de validité

Édition **complète pour son périmètre documentaire**, non qualification runtime de cluster. Aucun déploiement, restore, quorum failure, migration CRD sur API server ni démonstration HA n'a été exécuté sur le CRC. Les scénarios de banque et résultats sur papier ne sont pas des mesures réelles.

L'architecture d'installation détaillée sera traitée dans le Volume 03; les incidents opérationnels avancés et la résilience pratique seront abordés dans les autres volumes.

## Sources et droits

© 2026 Zidane Djamal pour les créations originales, **tous droits réservés** pour cette édition en l'absence de licence expresse; respect des droits tiers. Red Hat/OpenShift appartiennent à leurs titulaires respectifs. Ouvrage indépendant.

Voir [le rapport technique et les limites](V02_TECHNICAL_AUDIT_20261012.md), [l'avis au lecteur](V02_1_2_READER_NOTICE.md), [l'erratum](ERRATA_V01_V02_20261011.md) et [la politique de droits](RIGHTS_AND_LICENSING.md).

La pagination de ce PDF est informative; elle n'est pas un critère de clôture. Les éditions 1.0 et 1.1 sont conservées.
