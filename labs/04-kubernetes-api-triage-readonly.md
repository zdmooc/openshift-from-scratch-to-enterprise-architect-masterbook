# Lab V01-L04 — Comprendre l'API et diagnostiquer un workload sans modifier le cluster

**Statut : DOCUMENTED_NOT_RUN · Mode : READ_ONLY · Plateforme : OpenShift autorisé**  
**Pré-requis : client oc, contexte correct, droits de lecture adaptés.**

## A. Sécurité de la session

Ne pas afficher de tokens ni coller de kubeconfig. Si le namespace contient des informations confidentielles, publier uniquement des conclusions anonymisées. Ce lab n'utilise ni oc apply, ni delete, ni rollout restart, ni patch, ni debug/privileged.

## B. API et état plateforme

~~~bash
oc version
oc get clusterversion
oc get nodes
oc get clusteroperators
oc api-resources --namespaced=true
~~~

Question : quelles ressources appartiennent à l'API de base et quelles ressources sont des extensions de la plateforme ?

## C. Un namespace connu (remplacer NAMESPACE)

~~~bash
oc -n NAMESPACE get deployments
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE get services
oc -n NAMESPACE get endpointslices
oc -n NAMESPACE get routes
oc -n NAMESPACE get networkpolicies
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

Question : peut-on relier Deployment → ReplicaSet → Pod → Service → EndpointSlice ? Réponse : en comparant labels/selectors, ownerReferences, nombre de replicas prêts, et endpoints éligibles.

## D. Diagnostic ciblé

~~~bash
oc -n NAMESPACE describe deployment NOM_DEPLOYMENT
oc -n NAMESPACE describe pod NOM_POD
oc -n NAMESPACE get pod NOM_POD -o jsonpath='{.spec.nodeName}{"\n"}{.status.phase}{"\n"}'
oc -n NAMESPACE get resourcequota,limitrange
~~~

Les résultats dépendent des droits. `phase=Running` n'est pas synonyme d'API métier opérationnelle.

## E. Questions

1. Le nombre de réplicas désirés correspond-il aux réplicas Ready et Available ?
2. Les labels des Pods correspondent-ils aux sélecteurs des Services ?
3. Une Route sans backend Ready est-elle un incident de DNS ou de Pod ?
4. Les Events mentionnent-ils un problème de scheduler, d'admission ou d'image ?
5. Les requests / limits sont-ils cohérents avec la capacité allocatable ?

## F. Résultat attendu et limites

Produire un tableau **fait → preuve → hypothèses restantes**, jamais une affirmation sans observation. Ce lab n'a pas été exécuté dans le cadre de sa rédaction.
