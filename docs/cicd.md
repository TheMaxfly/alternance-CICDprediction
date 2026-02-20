# Pipeline CI/CD

## Vue d'ensemble

```
feature/* ──PR──▶ develop ──PR──▶ main
                    │                │
                   CI            CI + Release
                    │                │
              pre-commit          Semantic
              lint / type         Release
              security            ↓
              tests            Docker → GHCR
```

## Workflows GitHub Actions

### CI (`.github/workflows/ci.yml`)

Déclenché sur chaque push et pull request vers `develop` ou `main`.

| Job | Outil | Description |
|---|---|---|
| lint | Ruff | Vérification du style et des imports |
| typecheck | Pyright | Vérification des types |
| security | Bandit + pip-audit | Analyse statique + vulnérabilités |
| tests | pytest | Tests unitaires avec couverture |
| pre-commit | pre-commit | Vérification des hooks |

### Build Docker (`.github/workflows/build.yml`)

Déclenché sur push vers `develop`/`main` et PR vers `main`.

- Build image API (`briefml-api`) → GHCR
- Build image Streamlit (`briefml-streamlit`) → GHCR
- Tags : branche, SHA court, `latest` sur `main`

### Semantic Release (`.github/workflows/release.yml`)

Déclenché après succès de la CI sur `main`.

1. Analyse les commits conventionnels
2. Calcule la nouvelle version (MAJOR/MINOR/PATCH)
3. Bumpe la version dans `pyproject.toml`
4. Génère le `CHANGELOG.md`
5. Crée un tag Git et une GitHub Release

### Sync Develop (`.github/workflows/sync-develop.yml`)

Déclenché sur création d'un tag `v*`.

Merge automatiquement `main` dans `develop` pour rester synchronisés.

## Conventional Commits

| Type | Effet sur la version |
|---|---|
| `feat:` | MINOR bump (0.1.0 → 0.2.0) |
| `fix:`, `perf:` | PATCH bump (0.1.0 → 0.1.1) |
| `feat!:` / `BREAKING CHANGE` | MAJOR bump (0.1.0 → 1.0.0) |
| `chore:`, `ci:`, `docs:`, `style:` | Aucun bump |

## Pre-commit Hooks

Exécutés localement avant chaque `git commit` :

- Trailing whitespace / end of file
- Détection de clés privées
- Conflits de merge
- Ruff (lint + format automatique)
