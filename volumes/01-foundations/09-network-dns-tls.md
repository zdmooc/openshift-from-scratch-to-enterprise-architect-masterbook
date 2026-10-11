# 09 — Réseau Kubernetes/OpenShift : DNS, Services, flux TLS et diagnostic N3

**Volume 01 · Statut EDITION_1_CONTENT_COMPLETE · Base documentaire OCP 4.22 / Kubernetes**  
**Niveau de preuve : PUBLIC_VERIFIED pour les mécanismes documentés ; aucun test CRC dans cette itération.**

## 1. Objectifs

Être capable de reconstruire le parcours complet d'un appel HTTP de l'extérieur jusqu'au conteneur, de distinguer une résolution DNS d'un routage de paquets, d'identifier l'emplacement des NetworkPolicies et du point de terminaison TLS, et de diagnostiquer en lecture seule la perte de disponibilité d'un Service.

Le volume 04 traitera OVN-Kubernetes en profondeur. Le présent chapitre établit le langage commun nécessaire à l'architecte et à l'exploitation.

## 2. Trois plans réseau distincts

| Plan | Exemple | Question à résoudre |
|---|---|---|
| Réseau des nœuds | IP du worker, accès API/LB, route physique | Les machines et les infrastructures communiquent-elles ? |
| Réseau des Pods | IP des Pods, CNI, NetworkPolicy, egress | Les workloads peuvent-ils joindre les destinations autorisées ? |
| Réseau des Services | DNS, ClusterIP, EndpointSlices, routage ingress | Comment trouver et atteindre les backends actuellement éligibles ? |

Ces plans se recouvrent mais ne doivent pas être confondus. Un Service stable masque le renouvellement d'IP des Pods; il ne remplace ni une base de données persistante ni les mesures SLI métier.

### 2.1 Parcours logique d'une requête

~~~mermaid
sequenceDiagram
  participant C as Client HTTPS
  participant DNS as DNS externe
  participant LB as LB / routeur OpenShift
  participant S as Service interne
  participant E as Endpoints éligibles
  participant A as Application Pod
  C->>DNS: Résolution api.example
  DNS-->>C: Adresse du point d'entrée
  C->>LB: TCP/TLS / HTTP
  LB->>S: Choix du Service cible
  Note over S,E: Modèle logique, pas saut réseau littéral
  S->>E: Sélection backend issue des endpoints
  E->>A: Trafic applicatif via dataplane
  A-->>C: Réponse du service (selon proxy/TLS)
~~~

La sélection des endpoints et la translation de paquets sont réalisées par le dataplane/controller approprié. L'objet Kubernetes **EndpointSlice n'est pas lui-même un proxy traversé par les paquets**.

## 3. DNS : nom stable, résolution conditionnelle

Un Service Kubernetes de type ClusterIP nommé \`payments\` dans le namespace \`banking\` est généralement résolu via :

- \`payments\` depuis un Pod **dans banking**, grâce à la liste de recherche DNS ;
- \`payments.banking\` depuis un autre namespace, selon configuration ;
- \`payments.banking.svc.cluster.local\` en FQDN si le domaine de cluster est \`cluster.local\`.

**Attention :** \`cluster.local\` est usuel, mais pas universel. Vérifier le domaine DNS du cluster. Le serveur DNS peut répondre A ou AAAA selon le cluster et le Service.

Un Service **headless** utilise \`clusterIP: None\` et expose des enregistrements vers ses endpoints plutôt qu'une IP de Service virtuelle unique. Cette différence est importante pour StatefulSets et certains clusters de bases/brokers : les clients peuvent devoir gérer plusieurs adresses.

### 3.1 Le DNS Operator OpenShift

Sur OCP 4.22, le DNS Operator gère CoreDNS et expose notamment \`dns.operator/default\`. Les premières vérifications en lecture seule sont :

~~~bash
oc get clusteroperator/dns
oc -n openshift-dns-operator get deployment/dns-operator
oc -n openshift-dns get daemonsets
oc describe dns.operator/default
~~~

Ces commandes peuvent être interdites par RBAC et afficher des noms internes. Il faut travailler avec l'accès autorisé et **ne jamais exposer de kubeconfig**.

Ne pas « réparer » une panne de résolution en éditant le \`/etc/resolv.conf\` d'un nœud OpenShift : les nœuds sont gérés et la configuration DNS des Pods dépend des mécanismes kubelet/DNS Operator. Une modification manuelle non supportée est une dette opérationnelle.

### 3.2 Matrice de diagnostic DNS

| Symptôme | Hypothèse | Contrôle read-only |
|---|---|---|
| \`payments\` fonctionne dans banking, pas ailleurs | Namespace implicite | Nom pleinement qualifié |
| FQDN interne ne résout plus partout | CoreDNS / service DNS / policy | ClusterOperator DNS, DaemonSet, Events |
| Un nom externe échoue seulement dans un namespace | Policy egress, resolver externe | NetworkPolicy et état DNS dans ce namespace |
| L'adresse résout mais connexion échoue | Ce n'est probablement plus une panne DNS | Service, endpoints, ports, NetworkPolicy |
| Un Pod ancien ne prend pas un changement de résolveur | Config Pod / lifecycle | \`dnsPolicy\`, options DNS, config de résolution |

Le diagnostic DNS impose de regarder les **noms demandés**, pas seulement d'essayer un ping. Un nom résolu ne prouve pas qu'un service fonctionne.

## 4. Service, EndpointSlices et ports : contrat de cohérence

Un Service associe une sélection de Pods à un ou plusieurs ports. Exemple pédagogique :

~~~yaml
apiVersion: v1
kind: Service
metadata:
  name: payments
  namespace: banking
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: payments
  ports:
  - name: http
    port: 80
    targetPort: http
~~~

Cette ressource peut être syntaxiquement correcte tout en étant **non fonctionnelle** si aucun Pod ne porte le bon label, si le port nommé \`http\` n'existe pas, si la readiness échoue ou si une NetworkPolicy bloque le trajet.

### 4.1 Ce que l'EndpointSlice prouve

Un EndpointSlice peut décrire des adresses, des ports et des conditions d'endpoints. Observer des endpoints prêts est un indice que le Service a des backends candidats. **Ce n'est pas un test HTTP, ni un test d'autorisation métier.**

~~~bash
oc -n banking get svc payments -o yaml
oc -n banking get endpointslices -l kubernetes.io/service-name=payments
oc -n banking get pods -l app.kubernetes.io/name=payments -o wide
~~~

Ne présumez pas que les permissions de lecture d'EndpointSlices sont identiques aux droits sur les Services.

## 5. Entrée du cluster : DNS/LB/Ingress/Route

L'arrivée d'un appel externe suppose plusieurs contrats :

1. Le DNS du client pointe vers le point d'entrée.
2. Le firewall et le load balancer autorisent les réseaux attendus.
3. L'Ingress Controller possède une configuration saine.
4. Une Route/Ingress correspond à l'hôte, au chemin et au Service.
5. Le Service a des endpoints adéquats.
6. L'application écoute et répond sur le port attendu.
7. Les contrôles TLS et d'identité du client et du backend sont cohérents.

### 5.1 Terminaisons TLS OpenShift

| Mode | TLS client → routeur | TLS routeur → backend | Contrôle dominant |
|---|---|---|---|
| edge | Oui | Généralement HTTP sans chiffrement | Exigence de confiance sur réseau intérieur |
| reencrypt | Oui | Nouvelle liaison TLS | CA du backend et nom de certificat |
| passthrough | Traverse routeur | TLS au backend | Certificats gérés par application, SNI |

Un Route edge **ne chiffre pas automatiquement** le hop routeur → application. Pour une obligation de chiffrement jusqu'au backend, ce choix est insuffisant sans mécanisme additionnel.

### 5.2 Scénarios 503, 502 et 504

L'origine de la réponse importe plus que le seul code :

- **503** : absence de backend éligible ou indisponibilité à la couche routeur/service, selon la topologie.
- **502** : problème de communication backend / réponse invalide, selon proxy.
- **504** : timeout d'un intermédiaire ou d'une dépendance.

Il faut relier le timestamp, la Route, le Service, la condition Ready et les logs des couches concernées. Ces codes ne permettent pas d'attribuer mécaniquement la faute à OpenShift.

## 6. NetworkPolicy : modèle des flux autorisés

Les NetworkPolicies utilisent des sélecteurs sur des Pods et des namespaces pour exprimer la connectivité voulue. Les règles sont **additives** : lorsqu'un Pod est isolé dans une direction, une connexion est permise si les politiques concernées autorisent le trafic selon les critères applicables; ajouter une policy « allow-all » peut donc court-circuiter l'intention d'isolation.

**Default deny** :

~~~yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: banking
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  ingress: []
  egress: []
~~~

Ce manifeste est **à ne pas appliquer tel quel** à un namespace partagé : il peut interrompre DNS, télémétrie et applications. L'exemple démontre uniquement la portée de \`podSelector: {}\` et des directions isolées.

### 6.1 Point spécifique OCP 4.22

Depuis OCP 4.22, des NetworkPolicies de moindre privilège sont gérées dans certains namespaces réseau critiques d'OpenShift, notamment ceux du DNS et de l'Ingress. Red Hat prévient que des Pods personnalisés non gérés dans ces namespaces peuvent se retrouver bloqués. Il ne faut donc **jamais** utiliser \`openshift-dns\` ni \`openshift-ingress\` comme emplacement d'exercices personnels.

Cette règle évite un anti-pattern fréquent : placer un outil de debug dans un namespace système pour « être proche » d'un composant; cela modifie le risque et perturbe les hypothèses de support.

## 7. Diagnostic read-only en cinq frontières

Sur un namespace applicatif autorisé :

~~~bash
oc -n NAMESPACE get route,svc,pod
oc -n NAMESPACE get endpointslices
oc -n NAMESPACE get networkpolicies
oc -n NAMESPACE get events --sort-by=.lastTimestamp
oc get clusteroperator/dns
oc get clusteroperator/ingress
~~~

Puis classer l'incident :
- **Résolution :** nom incorrect ou service DNS ?
- **Entrée :** TLS, Route ou point d'entrée ?
- **Backends :** aucun endpoint prêt ou mauvais port ?
- **Réseau :** flux refusé par policy ou firewall ?
- **Application :** 401/403 métier, pool DB épuisé, dépassement de timeout ?

Un protocole N3 doit donner à chaque hypothèse **une observation discriminante** et une preuve horodatée. Ne pas changer simultanément DNS, NetworkPolicy et ingress; plusieurs mutations rendent l'attribution de cause difficile.

## 8. Atelier guidé sur papier

Une API répond 503 depuis l'extérieur. Deux Pods sont Running, mais \`get endpointslices\` montre zéro endpoint Ready. Dérouler les preuves :

1. Les labels Pod matchent-ils le selector Service ?
2. \`oc describe pod\` montre-t-il une readiness en échec ?
3. L'application écoute-t-elle le port effectivement référencé par \`targetPort\` ?
4. La Route pointe-t-elle vers le bon Service ?
5. Si tous les endpoints deviennent Ready et le 503 persiste, poursuivre vers ingress et connectivité.

**Corrigé** : tant que le Service n'a aucun backend prêt, modifier TLS ou DNS externe ne traite pas la condition nécessaire la plus proche de l'échec. Si le Service reste incorrect malgré des Pods Ready, examiner selector/ports avant NetworkPolicy.

## 9. Erreurs à bannir

- Assimiler l'IP d'un Service à l'IP fixe d'un Pod.
- Croire qu'une Route « Ready » valide la transaction bancaire.
- Proposer \`oc debug node\` ou un Pod privilégié pour chaque panne DNS.
- Conclure qu'une NetworkPolicy règle TLS ou les autorisations métier.
- Appliquer un default-deny sans inventorier les flux indispensables.
- Déduire le domaine de cluster \`cluster.local\` sans consulter la configuration réelle.

## Références et version

- [Red Hat — DNS Operator OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/networking_operators/dns-operator)
- [Red Hat — Network security OCP 4.22](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html-single/network_security/index)
- [Red Hat — OCP 4.22 Networking overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html-single/networking_overview/index)
- [Kubernetes — DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Kubernetes — Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes — Service](https://kubernetes.io/docs/concepts/services-networking/service/)

**Validation manquante :** tests sur namespace isolé autorisé, observation d'endpoints, comportement DNS et NetworkPolicy de la cible. Ce chapitre ne revendique aucune preuve RUNTIME_PROVEN.
