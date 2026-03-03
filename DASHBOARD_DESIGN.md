# Dashboard Design

## Objectif

Ce document décrit les choix de conception du dashboard Grafana réalisé pour le
projet BriefML, une application de prédiction de gravité d'accident basée sur
une API FastAPI.

L'objectif du dashboard est de fournir une vue exploitable de l'état du système
pendant l'exécution normale et pendant les tests de charge.

Le dashboard ne suit pas un CRUD "Items" classique ; il a été adapté au métier
de l'application :

- prédiction de risque d'accident grave,
- suivi des erreurs de validation utilisateur,
- suivi de la latence de l'inférence,
- suivi des ressources hôte et conteneurs.

## Public cible

Le dashboard vise principalement :

- un profil technique de type développeur backend / DevOps,
- un profil orienté performance / exploitation,
- un formateur ou évaluateur qui souhaite vérifier le comportement de
  l'application sous charge.

Ce dashboard n'est pas conçu comme un dashboard produit orienté métier pur,
mais comme un dashboard d'observabilité technique.

## Logique de conception

La conception repose sur trois niveaux de lecture :

1. **Applicatif**
   Suivi du volume de requêtes, des erreurs, de la latence et des résultats
   de prédiction.

2. **Infrastructure**
   Suivi du CPU, de la mémoire et du disque de la machine hôte via
   `node-exporter`.

3. **Conteneurs**
   Suivi du CPU, de la mémoire et du réseau des services Docker via `cAdvisor`.

Cette structure permet de relier un symptôme applicatif à une cause
infrastructurelle ou à un comportement d'un conteneur spécifique.

## Panels retenus

### Bloc applicatif

- `requete/min`
  Mesure le rythme de trafic sur l'endpoint `/predict`.
  Sert à suivre la montée en charge et la capacité observée.

- `Erreurs de validation / min`
  Mesure le volume de requêtes invalides (`422`) renvoyées par l'API.
  Permet d'identifier les erreurs côté saisie ou côté test.

- `Total erreurs HTTP`
  Mesure le volume total d'erreurs HTTP observées.
  Sert de compteur global d'incidents applicatifs.

- `Taux d'erreur %`
  Mesure la proportion d'erreurs HTTP par rapport au trafic total.
  Permet une lecture synthétique de la qualité de service.

- `Latence moyenne`
  Fournit une vision générale du temps de réponse.
  Utile mais insuffisant seul, car il lisse les pics.

- `Latence P95`
  Sert d'indicateur principal de performance perçue.
  Il a été retenu car il révèle mieux les dégradations réelles que la moyenne.

- `Résultats par classe`
  Affiche la répartition des sorties du modèle (`grave` / `non_grave`).
  Ce panel constitue la métrique métier principale du dashboard.

- `Uptime application`
  Indique depuis combien de temps l'API tourne.
  Sert à vérifier les redémarrages et la stabilité du service.

### Bloc infrastructure (node-exporter)

- `CPU usage %`
  Suit la charge CPU globale de la machine.
  Permet de détecter une saturation hôte.

- `Memory usage %`
  Suit l'occupation mémoire de la machine.
  Permet de repérer une pression mémoire durable.

- `Disk usage %`
  Suit l'occupation du disque racine.
  Sert à détecter un risque d'épuisement de stockage.

### Bloc conteneurs (cAdvisor)

- `CPU par conteneur (%)`
  Affiche la consommation CPU de chaque conteneur de la stack.

- `Mémoire utilisée par conteneur (MB)`
  Affiche la mémoire consommée par conteneur.

- `Réseau reçu par conteneur (MB/s)`
  Affiche le trafic entrant par conteneur.

- `Réseau émis conteneurs projet (MB/s)`
  Affiche le trafic sortant par conteneur.

Ces panels ont été conçus pour ne suivre que les conteneurs du projet, en
filtrant sur le préfixe Compose `alternance-cicdprediction-*`.

## Choix de visualisation

Les visualisations ont été choisies selon la nature des données :

- `Time series`
  Pour les tendances dans le temps :
  requêtes/min, erreurs/min, latence, CPU, réseau.

- `Gauge`
  Pour les valeurs instantanées de type pourcentage :
  mémoire, disque, parfois uptime ou taux d'erreur selon les variantes.

- `Table`
  Pour la mémoire par conteneur, afin de comparer les valeurs instantanées.

Ces choix suivent la logique du brief :

- tendance = courbe,
- état courant = gauge ou stat,
- comparaison de plusieurs entités = table ou séries multiples.

## Organisation visuelle

Le dashboard est organisé pour favoriser une lecture de haut en bas :

1. lecture immédiate de la santé applicative,
2. lecture de la performance,
3. lecture des ressources machine,
4. lecture des ressources conteneurs.

L'idée est de commencer par le symptôme visible côté API, puis de descendre vers
la cause potentielle côté infrastructure.

## Adaptation par rapport au brief d'origine

Le brief d'origine reposait sur une API CRUD de type `Items`.

Dans ce projet, les métriques ont été adaptées à une API de prédiction :

- les compteurs CRUD ont été remplacés par des métriques de trafic de prédiction,
- la logique métier suit le résultat du modèle (`grave` / `non_grave`),
- les erreurs observées sont principalement des erreurs de validation (`422`)
  et des erreurs HTTP de service,
- la latence observée correspond à l'inférence du modèle, pas à des opérations
  de base de données CRUD.

Cette adaptation respecte l'esprit du brief tout en l'alignant sur le métier
réel de l'application.

## Limites actuelles

- Certains panels peuvent afficher `No data` juste après un redémarrage si aucun
  trafic n'a encore été généré.
- Les métriques `cAdvisor` dépendent du nom réel des conteneurs Docker ; un
  changement de stratégie de nommage impose de mettre à jour les requêtes.
- L'API n'étant pas toujours lancée dans le même mode (local ou Compose), les
  dashboards peuvent nécessiter une adaptation légère selon le contexte.


