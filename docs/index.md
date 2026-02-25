# BriefML — Prédiction d'accidentologie

![CI](https://github.com/TheMaxfly/alternance-CICDprediction/workflows/CI/badge.svg)
![Build](https://github.com/TheMaxfly/alternance-CICDprediction/workflows/Build%20%26%20Push%20Docker%20Images/badge.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Présentation

**BriefML** est une application de prédiction de la gravité des accidents de la route en France, développée dans le cadre d'un brief CI/CD professionnel.

Elle combine :

- **CatBoost** — modèle de gradient boosting entraîné sur les données d'accidentologie 2022–2024
- **FastAPI** — API REST pour les prédictions en temps réel
- **Streamlit** — interface utilisateur interactive

## Architecture

```
briefml/
├── api/
│   └── predictor.py     → API FastAPI (endpoint /predict)
└── ui/
    ├── app.py           → Entrée Streamlit
    ├── pages/           → 6 pages de formulaire
    └── lib/             → Client API, validation, modèles
```

## Pipeline CI/CD

```
feature/* → develop → main
               ↓          ↓
              CI       Semantic Release
                           ↓
                       Docker → GHCR
```

## Liens rapides

- [Guide de démarrage](getting-started.md)
- [Documentation API](api/predictor.md)
- [Changelog](changelog.md)
