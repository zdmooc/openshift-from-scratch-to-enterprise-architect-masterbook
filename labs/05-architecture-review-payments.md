# Lab V01-L05 — Revue d'architecture d'une API bancaire sur OpenShift

**Mode : PAPER_LAB · Status : REFERENCE_ARCHITECTURE**

## Enoncé

Une API de lecture bancaire doit fonctionner sur OpenShift. Elle reçoit un trafic variable, s'authentifie via OIDC, interroge une base externe et produit des événements d'audit. Elle doit supporter l'échec d'un Pod en production, assurer la confidentialité des données et permettre un rollback applicatif. Le laboratoire disponible est un CRC mono-nœud.

## Travail demandé

1. Proposer un schéma indiquant : client, ingress, service, pods, identité, base externe, logs/traces et route egress.
2. Expliquer le rôle de chaque frontière et les flux qui doivent être autorisés.
3. Définir un contrat de service : 3 SLI et les mesures pour les collecter; **ne pas inventer de SLO client**.
4. Proposer des requests/limits initiales comme hypothèses, puis un protocole de mesure pour les ajuster.
5. Énoncer les exigences d'image : non-root, gestion des UID, écriture, secrets, provenance, signature.
6. Décrire le comportement d'une panne Pod, nœud, base ou identity provider.
7. Établir un plan de tests : nominal, refus RBAC, refus réseau, interruption dépendance, rollout, rollback.
8. Séparer les preuves possibles sur CRC de celles nécessitant un environnement multinœuds.

## Corrigé de référence

| Exigence | Architecture plausible | Preuve |
|---|---|---|
| Surface externe | Route/Ingress vers Service interne | DNS/TLS + code métier + flux vérifié |
| Exécution | Deployment stateless avec probes cohérentes | Rolling update et readiness observés |
| Identité | OIDC et validations dans l'API | Tests jeton absent/invalide/expiré |
| Accès aux dépendances | NetworkPolicies et identité technique dédiée | Tests flux positifs et négatifs |
| Durabilité | Données dans un service externe sauvegardé | Test restauration et intégrité distinct |
| Observabilité | Métriques, logs, traces et corrélation | Tableau SLI + test d'incident |
| Disponibilité | Replicas distribués sur domaines de panne disponibles | Test panne contrôlée multinœuds |
| Sécurité runtime | SCC adaptée et processus non-root | Admission, droits et tests filesystem |
| Livraison | Image à digest figé, provenance et GitOps | Audit du commit jusqu'au cluster |
| Réversibilité | Rollback versionné, compatibilité données | Drill incluant migrations |

## Décisions d'architecture

**ADR-01 : déployer l'API stateless via Deployment.** Les Pods sont interchangeables; aucun état local durable n'est supposé.  
**ADR-02 : encapsuler les dépendances externes derrière des contrats explicites.** Circuit breakers, timeouts et stratégies de dégradation métier doivent être déterminés.  
**ADR-03 : privilégier l'UID non-root et une SCC restrictive.** Des exceptions documentées requièrent une analyse de risque.  
**ADR-04 : ne pas déclarer de HA ou DR sur la seule preuve CRC mono-nœud.** Un test multi-domaines est obligatoire pour le valider.

## Questions de soutenance

- Que devient l'API si l'OIDC est indisponible après émission du jeton ?
- Pourquoi trois replicas peuvent-ils être inutiles devant une base SPOF ?
- Les ServiceEndpoints sont-ils une preuve de succès fonctionnel ?
- Quels tests négatifs protègent des hypothèses fausses de segmentation ?
- Quel volet du rollback est hors du contrôle du Deployment ?

## Conclusion

L'exercice est réussi lorsque chaque choix est rattaché à une exigence mesurable, une méthode de preuve et un mode de panne. **Aucun test CRC n'a été effectué pour cette fiche.**
