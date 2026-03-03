# Checklist Demo Monitoring

Cette checklist sert a valider rapidement la stack de monitoring, l'affichage des metriques, et les alertes Discord avant et pendant la presentation.

## 1. Avant la demo

- Verifier que le fichier `secrets/discord_webhook_url` est bien present localement.
- Verifier que le fichier `.env` est bien present localement.
- Se placer a la racine du projet :

```bash
cd /home/maxime/simplonalternance/alternance-CICDprediction
```

## 2. Lancer toute la stack

- Lancer la stack complete :

```bash
./scripts/start_monitoring.sh
```

- Variante avec Locust prete :

```bash
./scripts/start_monitoring.sh --with-locust
```

## 3. Verifier l'etat Docker

- Verifier les conteneurs :

```bash
docker compose ps
```

- Tous les services doivent etre `Up`.
- Les services avec healthcheck doivent etre `healthy` :
  - `api`
  - `mlflow`
  - `postgres`
  - `streamlit`
  - `cadvisor`

## 4. Verifier les interfaces principales

- API health :
  - `http://localhost:8000/health`
- API metrics :
  - `http://localhost:8000/metrics`
- Streamlit :
  - `http://localhost:8501`
- MLflow :
  - `http://localhost:5000`
- Prometheus targets :
  - `http://localhost:9090/targets`
- Prometheus alerts :
  - `http://localhost:9090/alerts`
- Grafana :
  - `http://localhost:3000`
- Alertmanager :
  - `http://localhost:9093`
- Uptime Kuma :
  - `http://localhost:3001`

## 5. Verifier Prometheus

- Dans `http://localhost:9090/targets`, verifier que ces targets sont `UP` :
  - `fastapi`
  - `node-exporter`
  - `cadvisor`
  - `prometheus`

- Dans `http://localhost:9090/rules`, verifier que les regles existent :
  - `HighErrorRate`
  - `HighLatencyP95`
  - `FastApiTargetDown`

## 6. Verifier Grafana

- Ouvrir le dashboard principal.
- Verifier que les panels principaux affichent des donnees :
  - requetes
  - latence
  - erreurs
  - CPU / memoire
  - conteneurs

- Si certains panels sont vides, faire 2 a 3 requetes `/predict`, puis rafraichir.

## 7. Verifier Uptime Kuma

- Verifier que les sondes critiques sont `UP` :
  - `API health`
  - `Prometheus`
  - `Grafana`
  - `Alertmanager`
  - `MLflow`

- Verifier que la notification Discord est bien associee a la sonde `API health`.

## 8. Test applicatif rapide

- Verifier une prediction valide :

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data":{"dep":"59","lum":1,"atm":1,"catr":3,"agg":2,"int":1,"circ":2,"col":3,"vma_bucket":"51-80","catv_family_4":"voitures_utilitaires","manv_mode":1,"driver_age_bucket":"25-34","choc_mode":1,"driver_trajet_family":"trajet_1","time_bucket":"morning_06_11"}}'
```

- Verifier une prediction invalide (pour alimenter les erreurs `422`) :

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"data":{"dep":"59"}}'
```

- Attendre 15 a 30 secondes, puis rafraichir Grafana.

## 9. Test d'alerte Discord (panne)

Objectif :
- valider Uptime Kuma -> Discord
- valider Prometheus -> Alertmanager -> Discord

### 9.1 Provoquer la panne

- Arreter temporairement l'API :

```bash
docker compose stop api
```

### 9.2 Verifier les effets attendus

- Dans Uptime Kuma :
  - `API health` doit passer `DOWN`
- Dans Prometheus :
  - `FastApiTargetDown` doit passer `pending`, puis `firing`
- Dans Discord :
  - recevoir un message de panne venant d'Uptime Kuma
  - recevoir un message d'alerte venant d'Alertmanager

### 9.3 Temps d'attente

- Attendre environ 1 min 15 a 1 min 30 pour laisser :
  - la sonde Uptime Kuma detecter la panne
  - la regle Prometheus passer le `for: 1m`

## 10. Test d'alerte Discord (retablissement)

### 10.1 Relancer l'API

```bash
docker compose start api
```

### 10.2 Verifier les effets attendus

- Dans Uptime Kuma :
  - `API health` doit repasser `UP`
- Dans Prometheus :
  - `FastApiTargetDown` doit quitter l'etat `firing`
- Dans Discord :
  - recevoir le message de retablissement Uptime Kuma
  - recevoir le message de resolution Alertmanager

## 11. Test Locust (optionnel)

- Si Locust n'est pas deja lance :

```bash
uv run locust -f locustfile.py --host http://localhost:8000
```

- Ouvrir :
  - `http://localhost:8089`

- Lancer un petit palier de charge :
  - `20` users
  - spawn rate `2`

- Montrer dans Grafana :
  - requetes / min
  - latence P95
  - taux d'erreur

## 12. Fin de demo

- Si tu veux simplement fermer proprement en gardant les donnees :

```bash
docker compose down
```

- Ne pas utiliser `docker compose down -v` si tu veux conserver :
  - dashboards Grafana
  - historique Prometheus
  - sondes Uptime Kuma
  - configuration Alertmanager
  - donnees PostgreSQL / MLflow

## 13. Plan B si un service ne repond pas

- Refaire un etat rapide :

```bash
docker compose ps
```

- Relancer un service unique :

```bash
docker compose restart api
docker compose restart prometheus
docker compose restart alertmanager
docker compose restart uptime-kuma
```

- Si besoin, relancer toute la stack :

```bash
docker compose down
./scripts/start_monitoring.sh
```
