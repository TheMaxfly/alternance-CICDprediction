# Rapport de Stress Test

## Contexte

Ce rapport synthétise les tests de charge réalisés sur l'API FastAPI de prédiction
de gravité d'accident (`POST /predict`) du projet BriefML.

L'objectif était de :

- vérifier la stabilité de l'API sous charge,
- observer l'impact sur les métriques applicatives et infrastructure,
- identifier un point de rupture ou, à défaut, une limite de capacité observable.

Les observations ont été réalisées avec :

- `Locust` pour la génération de charge,
- `Prometheus` pour la collecte des métriques,
- `Grafana` pour la visualisation,
- `node-exporter` pour les métriques hôte,
- `cAdvisor` pour les métriques conteneurs.

## Périmètre du test

Le scénario Locust cible uniquement l'endpoint `POST /predict` avec deux profils :

- requêtes valides attendues en `200`,
- requêtes invalides attendues en `422`.

La répartition du trafic a été configurée ainsi :

- 80% de requêtes valides,
- 20% de requêtes invalides.

Deux phases de test ont été menées :

1. scénario initial avec `wait_time = between(1, 3)`,
2. scénario plus agressif avec `wait_time = between(0.1, 0.5)`.

## Métriques suivies

Les indicateurs principaux observés pendant les tests :

- `Requêtes / min`,
- `Taux d'erreur %`,
- `Erreurs de validation / min`,
- `Latence moyenne`,
- `Latence P95`,
- `CPU usage %` (hôte),
- `Memory usage %` (hôte),
- `Requests/s` et `Failures %` dans Locust.

## Résultats observés

### Phase 1 — Scénario initial (`wait_time = 1 à 3 s`)

| Charge | RPS | Failures | P95 | CPU hôte | Mémoire hôte | Observation |
|---|---:|---:|---:|---:|---:|---|
| 200 users | 97.5 | 0% | 0.0210 s | ~20% | ~75% | Charge stable, aucune erreur |
| 400 users | 188 | 0% | 0.0299 s | stable | stable | Débit en hausse, système toujours stable |

Conclusion intermédiaire :

- l'API reste stable à 400 utilisateurs,
- la latence reste faible,
- aucun échec n'est observé.

### Phase 2 — Scénario agressif (`wait_time = 0.1 à 0.5 s`)

| Charge | RPS | Failures | P95 | CPU hôte | Mémoire hôte | Observation |
|---|---:|---:|---:|---:|---:|---|
| 300 users | 194 | 0% | 0.0495 s | ~30% | ~75% | Toujours stable sous charge plus dense |
| 500 users | 181 | 0% | ~0.050 s | ~30% | ~75% | Débit en léger recul, pas de dégradation visible |
| 700 users | 190 | 0% | stable | stable | stable | Confirmation d'un plateau de débit |

## Analyse

### Stabilité applicative

L'API est restée stable sur l'ensemble des paliers testés :

- aucun `failure` Locust observé,
- aucune explosion de latence,
- aucune erreur serveur remontée pendant les tests,
- `P95` maintenue dans une plage faible, autour de 20 à 50 ms.

### Limite de capacité observée

Aucun point de rupture brutal n'a été observé.

En revanche, un plateau de débit apparaît clairement :

- autour de 300 users agressifs, le débit est d'environ 194 RPS,
- à 500 et 700 users, le débit reste dans une zone proche de 180 à 195 RPS.

Cela signifie que :

- l'ajout d'utilisateurs supplémentaires n'augmente plus sensiblement le débit,
- une limite de throughput est atteinte dans ce contexte de test local,
- cette limite est observable sans dégradation forte de la latence ni apparition d'erreurs.

### Interprétation infrastructure

Les métriques hôte restent relativement stables :

- CPU hôte autour de 20% à 30%,
- mémoire hôte autour de 75%.

Ces mesures doivent être interprétées avec prudence :

- `node-exporter` mesure toute la machine, pas uniquement l'API,
- d'autres conteneurs tournaient sur la machine au moment des tests,
- l'API FastAPI n'était pas conteneurisée, donc elle n'apparaît pas dans les métriques `cAdvisor`.

En conséquence, la limite observée peut provenir de plusieurs facteurs :

- le client de charge Locust,
- le scénario de test,
- la pile réseau locale,
- l'environnement global de la machine,
- et pas exclusivement de l'API elle-même.

## Conclusion

Dans le cadre de ce test local :

- aucune rupture franche n'a été observée,
- l'API supporte jusqu'à 700 utilisateurs simulés sans erreur,
- la latence P95 reste faible,
- le débit plafonne autour de 180 à 195 requêtes/seconde.

La principale conclusion est donc la suivante :

> le système reste stable sous charge, mais une limite de capacité observable
> apparaît sous la forme d'un plateau de throughput, sans effondrement brutal.

## Pistes d'amélioration

- Conteneuriser aussi l'API pour mesurer son CPU et sa mémoire via `cAdvisor`.
- Exécuter Locust depuis une machine distincte pour éviter que le générateur de charge
  partage les mêmes ressources que la cible.
- Réduire encore le `wait_time` ou utiliser un mode Locust plus agressif pour chercher
  une rupture plus franche.
- Ajouter des métriques de temps d'inférence plus fines côté API si l'analyse de
  performance doit être approfondie.
- Conserver les résultats par palier dans un tableau de comparaison pour documenter
  les évolutions entre scénarios.
