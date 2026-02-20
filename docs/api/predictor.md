# API Prédicteur

Documentation automatique du module `briefml.api.predictor`.

## Endpoints

### `GET /health`

Vérifie que l'API est opérationnelle.

**Réponse** :
```json
{"status": "ok"}
```

### `POST /predict`

Prédit la gravité d'un accident à partir de ses caractéristiques.

**Corps de la requête** : voir [Dictionnaire API](../api_dictionary.md) pour la description des 15 features.

**Réponse** :
```json
{
  "prediction": 1,
  "probability": 0.73,
  "label": "Accident grave"
}
```

## Module

::: briefml.api.predictor
    options:
      show_source: true
      heading_level: 3
      members:
        - app
        - predict
        - health
