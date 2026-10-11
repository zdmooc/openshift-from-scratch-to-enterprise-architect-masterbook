# 10 — Stockage Kubernetes/OpenShift : PV, PVC, CSI, StatefulSet et restore

**Volume 01 · Statut EDITION_1_CONTENT_COMPLETE · Périmètre pédagogique : concepts Kubernetes et OCP 4.22**  
**Preuves : PUBLIC_VERIFIED pour les mécanismes ; REFERENCE_ARCHITECTURE pour les exemples.**

## 1. Objectifs

Savoir différencier le disque éphémère d'un conteneur et un volume persistant, expliquer les responsabilités de StorageClass/PV/PVC/CSI, choisir un mode d'accès sans supposer que RWO protège des écritures concurrentes par Pods, décrire le parcours de restore et expliciter pourquoi un snapshot n'est pas à lui seul une sauvegarde applicative.

## 2. Éphémère ou durable : quel état survit à quoi ?

Le système de fichiers de la couche writable d'un conteneur n'est pas un stockage durable à utiliser pour une base transactionnelle. Le conteneur peut être détruit et recréé lors d'un rollout; ses écritures locales disparaissent selon la couche concernée.

Kubernetes modélise des volumes pour les Pods. Certains sont éphémères, d'autres sont liés à des ressources externes ou à des revendications persistantes. **PersistentVolume n'est pas synonyme de sauvegarde**, et répliquer des Pods ne réplique pas nécessairement les données.

~~~mermaid
flowchart LR
  APP[Application stateful] --> PVC[PersistentVolumeClaim]
  PVC --> PV[PersistentVolume]
  SC[StorageClass] --> PROV[Provisioner CSI]
  PROV --> PV
  PV --> STORAGE[Volume fourni par infrastructure]
  SNAP[VolumeSnapshot] --> STORAGE
~~~

Le schéma illustre une chaîne de ressources, pas une écriture directe du Pod dans les objets Kubernetes. Le vrai chemin d'I/O traverse le nœud, les mounts et le CSI / stockage.

## 3. Les quatre contrats à lire systématiquement

| Objet | Portée API | Fonction | Ce qu'il ne garantit pas |
|---|---|---|---|
| StorageClass | Cluster | Classe, provisioner, paramètres et binding mode | Performances sans mesure |
| PersistentVolume (PV) | Cluster | Ressource de capacité et access modes | Données sauvegardées ou répliquées |
| PersistentVolumeClaim (PVC) | Namespace | Demande de capacité/classe/access mode | Placement immédiat ni volume disponible |
| CSI driver | Plateforme | Intégration opérations stockage | Toutes les fonctionnalités pour tous les drivers |

**Dynamique** : le provisioner peut créer un PV pour un PVC selon la StorageClass. **Statique** : des PV peuvent exister à l'avance. Les deux modèles doivent tenir compte de l'identité du volume, de son contenu, de la politique de reclaim et de la disponibilité de l'infrastructure.

### 3.1 Immediate vs WaitForFirstConsumer

Une StorageClass \`Immediate\` peut entraîner le provisionnement/la liaison avant de connaître le Pod qui consommera le volume; cela peut engendrer des conflits topologiques dans des infrastructures zonées.

Avec \`WaitForFirstConsumer\`, le provisionnement/binding attend un consommateur permettant de tenir compte de la topologie et des contraintes de placement. Un PVC Pending dans ce cas n'est **pas automatiquement** une panne; interpréter les événements du PVC/Pod et le type de StorageClass.

## 4. Access modes — distinctions souvent mal comprises

| Mode | Idée principale | Piège fréquent |
|---|---|---|
| ReadWriteOnce (RWO) | Le volume peut être monté lecture/écriture par **un seul nœud** | Plusieurs Pods sur **ce même nœud** peuvent parfois accéder au volume |
| ReadWriteOncePod (RWOP) | Vise un accès lecture/écriture par **un seul Pod** pour les volumes CSI compatibles | Nécessite support CSI et versions de composants adéquates |
| ReadOnlyMany (ROX) | Lecture seule par plusieurs nœuds si driver le supporte | Ne permet pas une mise à jour de données |
| ReadWriteMany (RWX) | Lecture/écriture par plusieurs nœuds si le driver le supporte | Ne garantit pas l'atomicité métier ou le verrouillage applicatif |

Les modes expriment surtout des capacités de montage. La sûreté de données exige aussi une application prévue pour les accès concurrents, les garanties du stockage et les mécanismes de cohérence.

### Exemple de demande (NON DÉPLOYABLE sans adaptation)

~~~yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ledger-data
  namespace: training-storage
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: REPLACE_WITH_APPROVED_STORAGE_CLASS
  resources:
    requests:
      storage: 2Gi
~~~

Les 2 Gi sont **purement pédagogiques**. Aucune StorageClass cible n'a été choisie. Ne pas appliquer un PVC pour « tester » sur un CRC saturé : il peut créer un volume réel consommant de l'espace et difficile à récupérer.

## 5. Lifecycle d'un PVC : binding, mount, libération

Étapes logiques :

1. Demande PVC admise, puis identification de la StorageClass.
2. Provisionnement/binding d'un PV compatible.
3. Placement du Pod compatible avec la topologie volume.
4. Opérations mount/attach nécessaires avant démarrage du container.
5. I/O applicative, avec garanties dépendant du stockage.
6. Suppression/reprise : persistance contrôlée par les objets et politiques.
7. Reclaim : comportement suivant \`Retain\` / \`Delete\` et configuration réelle.

La politique de reclaim concerne le cycle de la **ressource volume** après libération de la claim; elle n'est pas un substitut à un protocole de sauvegarde et de restauration. La suppression d'un PVC peut rendre des données inaccessibles, voire mener à suppression du volume selon la politique. **Aucune suppression PVC/PV dans un atelier de lecture seule.**

## 6. Pourquoi StatefulSet ne garantit pas la HA d'une base

Un StatefulSet apporte des identités et conventions ordonnées de Pods, et peut gérer des revendications de volume via \`volumeClaimTemplates\`. Il n'implémente **pas automatiquement** :

- quorum ou consensus ;
- réplication transactionnelle ;
- rattrapage d'un replica déconnecté ;
- promotion sûre d'un leader ;
- sauvegarde applicativement cohérente ;
- résolution de conflits de données ;
- répartition sur des nœuds/zones indépendants.

Le choix StatefulSet doit suivre les exigences du logiciel d'état : PostgreSQL, MongoDB, broker, etc. Des Operators de bases peuvent encapsuler certaines opérations, mais la qualité et le niveau de support doivent être évalués individuellement.

### 6.1 Cas d'école : deux replicas sur CRC mono-nœud

Deux Pods reliés à des volumes séparés sur un seul nœud n'éliminent pas le SPOF du nœud. Le nombre de replicas n'établit ni une chaîne de réplication valide ni une capacité de restore.

## 7. CSI Snapshots : instantané n'est pas sauvegarde garantie

L'API Kubernetes \`VolumeSnapshot\` / \`VolumeSnapshotContent\` / \`VolumeSnapshotClass\` est fournie comme des CRDs et requiert les composants snapshot appropriés. Tous les CSI drivers ne supportent pas nécessairement cette opération.

Un snapshot de volume donne un état de stockage à un instant donné. Il **n'impose aucune garantie de cohérence applicative** : une base peut avoir des transactions en vol, des caches non vidés, une réplication asynchrone ou plusieurs volumes à coordonner.

### 7.1 Contrat d'une sauvegarde exploitable

- Point de cohérence défini (filesystem, crash-consistent, application-consistent).
- Périmètre exact (data, WAL/journaux, configs, secrets nécessaires, dépendances).
- Rétention et copie indépendantes du domaine de panne.
- Chiffrement, contrôle d'accès et rotation des clés.
- Procédure de restauration, tests d'intégrité et mesures RPO/RTO.
- Tests de restauration périodiques, y compris perte de site si c'est dans la cible.
- Preuve que l'environnement restauré peut réellement traiter ses transactions.

**Snapshot Ready=True n'équivaut pas à « RPO/RTO prouvés ».**

## 8. Diagnostic read-only d'un PVC Pending

~~~bash
oc -n NAMESPACE get pvc
oc -n NAMESPACE describe pvc NOM_PVC
oc get storageclass
oc get csidrivers
oc -n NAMESPACE get pods -o wide
oc -n NAMESPACE get events --sort-by=.lastTimestamp
~~~

Une inspection d'un PV lié peut nécessiter des droits supplémentaires :

~~~bash
oc get pv NOM_PV -o yaml
~~~

Hypothèses à départager :
- StorageClass inexistante ou provisioner défaillant.
- Absence de quota storage / demande interdite.
- Taille/mode d'accès non supporté.
- Binding \`WaitForFirstConsumer\` sans consommateur schedulable.
- Conflit de topologie nœud/zone.
- Driver CSI indisponible ou saturé.
- Volume existant conservé mais non compatible.

### 8.1 Volume attaché mais container bloqué

Un Pod peut rester dans un état d'attente de montage malgré un PVC Bound. Distinguer \`Bound\` (claim associée à un PV) des opérations attach/mount réussies sur le nœud. Les événements et le CSI peuvent fournir une explication; une redémarrage forcé ou suppression du PVC sans diagnostic est risqué.

## 9. ADR stockage : qui assume le RPO ?

Dossier minimal pour une base transactionnelle :

| Décision | Options | Preuve exigée |
|---|---|---|
| Support physique | SAN, CSI cloud, ODF/Ceph, autre | Mesures sous charge et défaillance |
| Classes | Performance, disponibilité, chiffrement | Contrat StorageClass validé |
| HA données | Réplication base, stockage ou combinaison | Tests failover/quorum |
| Sauvegarde | Logique, physique, snapshots, PITR | Restore et intégrité |
| Répartition | nœuds/zones/sites | Test réel de perte de domaine |
| Coût | IOPS, Gi-mois, sauvegardes, transfert | Modèle coût complet |
| Suppression | Retain/Delete, légal, purge | Tests et autorisations |

Une décision doit lier exigences du domaine métier, preuve de restauration et responsabilité. Un PV de 200 Gi déjà alloué n'est pas une preuve de 200 Gi de données utiles ou d'un besoin fonctionnel futur de cette taille.

## 10. Exercices de soutenance

**Q1 : un volume RWO peut-il être monté par deux Pods ?** Selon le driver et la topologie, deux Pods sur le même nœud peuvent partager un RWO. Si un seul Pod doit écrire, étudier RWOP et le design applicatif.

**Q2 : pourquoi PVC Bound et Pod Pending coexistent-ils ?** Le binding n'assure pas le scheduling ni le montage. Vérifier placement, volumes, ressources et Events.

**Q3 : pourquoi un snapshot de PostgreSQL ne suffit-il pas ?** Cohérence des transactions, fichiers WAL, état multi-volumes, objectif de récupération et test restore ne découlent pas du snapshot de volume seul.

**Q4 : faut-il supprimer un PVC « obsolete » sur CRC ?** Seulement après inventaire de son propriétaire, de sa reclaimPolicy et de son contenu, preuve de sauvegarde si nécessaire, et procédure explicite. La réponse par défaut dans ce livre est **non**.

**Q5 : un StatefulSet résout-il RPO/RTO ?** Non. Il gère des primitives d'identité; RPO/RTO sont des propriétés de continuité démontrées sur un système complet.

## Références et limites

- [Kubernetes — Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes — Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Kubernetes — Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [Kubernetes — StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Red Hat — OCP 4.22 Storage](https://docs.redhat.com/en/documentation/openshift_container_platform/4.22/html/storage/index)

**Tests runtime nécessaires** : identifier les classes, drivers, policies et versions **effectifs**, valider une restauration dans un environnement autorisé, ne pas extrapoler depuis CRC. Le chapitre ne prétend pas que des tests de backup/restore ont été exécutés.
