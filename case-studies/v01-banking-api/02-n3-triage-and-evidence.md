# V01-C02 — Runbook N3 en lecture seule : incident sur API bancaire

**Statut : RUNBOOK_DOCUMENTED_NOT_RUN · Cible : OCP 4.22 · READ_ONLY**

## 1. Déclencheur et contrôle de l'incident

Symptôme fictif : un partenaire constate des erreurs intermittentes sur une API de consultation de paiements. Il faut identifier un périmètre de panne sans provoquer de nouveaux changements, sans vider de files et sans exposer de données clients.

**Objectif des 15 premières minutes (horizon pédagogique, pas un SLA)** : établir le niveau de service réellement touché, la temporalité, les changements proches et les premières hypothèses. Aucun diagnostic sérieux ne doit commencer par `oc delete pod`.

| Question | Donnée nécessaire | Importance |
|---|---|---|
| Qui est touché ? | Partenaire, région, endpoint, périmètre anonymisés | Évite de généraliser une panne locale |
| Depuis quand ? | Début, fréquence, version du service | Oriente changement récent vs incident latent |
| Quelle transaction ? | Trace/correlation ID anonymisé | Relie couche HTTP, dépendances et messages |
| Quel impact ? | Taux de transactions réellement échouées, p95/p99 | Priorisation métier |
| Changement récent ? | Révisions Git, digest, certificat, politiques | Hypothèse de régression |

## 2. Préflight du diagnostic

Ne pas exécuter sur un cluster sans autorisation. Dans les exemples, remplacer `NAMESPACE`, `DEPLOYMENT`, `SERVICE`, `ROUTE`; respecter les droits en vigueur.

~~~bash
oc config current-context
oc version
oc get clusterversion
oc get nodes
oc get clusteroperators
~~~

Ces commandes sont des lectures. Elles peuvent néanmoins afficher noms de cluster ou d'infrastructure. Toute sortie diffusée hors du cercle autorisé doit être revue et anonymisée.

## 3. Niveau 1 — La plateforme est-elle dégradée ?

~~~bash
oc get nodes -o wide
oc get clusteroperators
oc get machineconfigpools
oc adm top nodes
~~~

### Interprétation

- **Node NotReady** : examiner impact de placement et réplication sans en conclure immédiatement que le cluster entier est indisponible.
- **ClusterOperator Degraded** : relever celui-ci, sa condition et les Events avant de relier causalement au service.
- **CPU/mémoire élevés** : comparer usage instantané à demandes et capacité allocatable.
- **`top` indisponible** : incident de métriques possible; cela ne prouve pas la panne de l'application.

## 4. Niveau 2 — Le workload est-il réellement disponible ?

~~~bash
oc -n NAMESPACE get deployment DEPLOYMENT -o wide
oc -n NAMESPACE describe deployment DEPLOYMENT
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc -n NAMESPACE get resourcequota,limitrange
~~~

Ne pas partager les Events bruts s'ils comportent des URL internes, arguments d'application ou noms sensibles.

### Arbre causal

1. `desiredReplicas > availableReplicas` : examiner rollout et Pods non prêts.
2. `Pending` : examiner scheduler, taints, requests, volumes.
3. `ImagePullBackOff` : image, authentification registre, proxy/CA.
4. `CrashLoopBackOff` : logs applicatifs, configuration, OOMKilled, start/liveness probes.
5. `Running/Ready` mais erreurs métier : poursuivre au niveau applicatif; ne pas conclure à une absence d'incident.

## 5. Niveau 3 — Le chemin réseau et les endpoints

~~~bash
oc -n NAMESPACE get svc SERVICE -o yaml
oc -n NAMESPACE get endpointslices -l kubernetes.io/service-name=SERVICE
oc -n NAMESPACE get routes ROUTE -o yaml
oc -n NAMESPACE get networkpolicies
~~~

Se demander :

- Le Service sélectionne-t-il les labels du Pod ?
- Le `targetPort` correspond-il au port réellement écouté ?
- Des endpoints Ready sont-ils observables ?
- L'hôte Route/Ingress, le certificat et le mode TLS sont-ils cohérents ?
- Les politiques réseau autorisent-elles les flux réellement nécessaires ?

Un Service sans endpoints justifie un diagnostic de sélecteur et readiness **avant** une modification de la Route.

## 6. Niveau 4 — Dépendances externes

Kubernetes n'expose pas automatiquement la santé du moteur de paiement, du broker MQ, de l'IdP ou de la base de données. Consulter leurs dashboards et journaux via les circuits autorisés. La corrélation est le point clé :

~~~text
TraceId transaction (pseudonymisé)
  ↳ accès HTTP entrant : duration, result, partner
  ↳ validation OIDC : résultat, cache JWKS
  ↳ requête référentiel : durée, timeouts, retries
  ↳ publication événement : ack, retry, dead-letter
  ↳ HTTP sortant : code et durée
~~~

Interdiction de publier des payloads de paiement, tokens, identifiants nominaux et PII dans le Masterbook. Une métrique de profondeur de file, seule, ne prouve pas une perte de message; il faut aussi considérer flux entrants, ack, rétention, consumers et mécanismes de dead-letter.

## 7. Niveau 5 — Changement et réversibilité

Examiner la révision GitOps et l'image digest déclarée. En phase read-only :

~~~bash
oc -n NAMESPACE get deployment DEPLOYMENT -o jsonpath='{.spec.template.spec.containers[*].image}{"\n"}'
oc -n NAMESPACE rollout history deployment/DEPLOYMENT
oc -n NAMESPACE get deployment DEPLOYMENT -o jsonpath='{.metadata.generation}{"\n"}{.status.observedGeneration}{"\n"}'
~~~

Le fait qu'une version antérieure existe dans un historique de rollout ne prouve pas que la restauration soit sûre : une migration DB ou un changement de contrat de message peut rendre le rollback incompatible. Toute action corrective doit suivre la procédure opérationnelle validée.

## 8. Tableau de discrimination des hypothèses

| Symptôme conjoint | Hypothèse prioritaire | Preuve discriminante | Contre-exemple |
|---|---|---|---|
| 503 + EndpointSlices vides | Readiness/selector | État Pod + labels + probes | Mauvais certificat externe |
| API Ready + 504 corrélés DB | Dépendance données lente | Durées SQL, pool et traces | Saturation ingress seule |
| Erreurs 401 sur un partenaire | Claims, issuer, audience, clés | Journaux de vérification et contrat de jeton | Généralisation « panne OCP » |
| Erreurs lors d'un rollout | Régression version/config | Chronologie digest et taux d'erreur | Erreurs antérieures au changement |
| Pods redémarrent + OOMKilled | Mémoire/limite | State terminated, metrics mémoire | Sous-dimensionnement CPU pur |
| Absence traces mais erreurs client | Défaut télémétrie ou propagation | Vérifier taux d'échantillonnage et instrumentation | Affirmer qu'aucune requête n'a existé |

## 9. Format minimal de rapport d'incident

~~~text
Incident ID : <interne>
Date/heure : <horodatage UTC, fuseau>
Périmètre : <composants, partenaires anonymisés>
Impact métier : <taux de transactions touchées, méthode>
Dernier changement : <revision/digest non sensibles>
Observations read-only : <commandes/queries, contexte, résultats nettoyés>
Hypothèses écartées : <preuves>
Cause probable : <niveau de confiance>
Cause confirmée : <si démontrée>
Décision : <responsable de la mesure>
Vérification du rétablissement : <SLI observé sur fenêtre précisée>
Risque résiduel : <dépendances et contrôles>
Actions préventives : <ADR/runbook/test à améliorer>
~~~

Ce runbook est **une procédure de référence**, pas un compte rendu d'incident exécuté. La validation sur des environnements autorisés et le processus d'incident de l'organisation sont obligatoires avant usage opérationnel.

## Sources

- [Kubernetes — Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Kubernetes — Services](https://kubernetes.io/docs/concepts/services-networking/service/)
- [OpenShift 4.22 — Architecture](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/architecture/architecture)
