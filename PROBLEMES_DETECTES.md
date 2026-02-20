# PROBLEMES_DETECTES.md — Audit qualité du projet BriefML

> Audit réalisé avec : **Ruff** (lint + format), **Pyright** (types), **Bandit** (sécurité), **pytest**
> Date : 2026-02-20

---

## Résumé

| Catégorie | Nombre de problèmes |
|-----------|-------------------|
| 🎨 Formatage | 12 |
| 📦 Imports | 10 |
| 🏷️ Types | 8 |
| 📝 Documentation | 6 |
| 🔒 Sécurité | 2 |
| ♻️ Code mort | 2 |
| **TOTAL** | **40** |

---

## 🎨 Formatage — 12 problèmes

### P01 — 30 fichiers non conformes au format Ruff
**Commande** : `uv run ruff format --check .`
**Impact** : Incohérence stylistique, diffs pollués, lisibilité réduite

Fichiers concernés :
- `briefml/api/predictor.py`
- `briefml/ui/app.py`
- `briefml/ui/lib/api_client.py`
- `briefml/ui/lib/models.py`
- `briefml/ui/lib/reference_loader.py`
- `briefml/ui/lib/session_state.py`
- `briefml/ui/lib/validation.py`
- `briefml/ui/pages/1_Contexte_Route.py`
- `briefml/ui/pages/2_Infrastructure.py`
- `briefml/ui/pages/3_Collision.py`
- `briefml/ui/pages/4_Conducteur.py`
- `briefml/ui/pages/5_Conditions.py`
- `briefml/ui/pages/6_Recap_Prediction.py`
- `scripts/start.py`
- Tous les fichiers `tests/` (16 fichiers)

### P02 — Ligne trop longue (> 88 chars) dans `predictor.py`
- **Ligne 2** (100 chars) : commentaire de module trop long
- **Ligne 39** (92 chars) : `DEFAULT_MODEL_PATH`
- **Ligne 40** (101 chars) : `DEFAULT_META_PATH`
- **Ligne 107** (127 chars) : message d'erreur dans `normalize_input()`
- **Ligne 134** (91 chars) : message d'erreur hint
- **Ligne 182** (91 chars) : `Field(...)` description
- **Ligne 195** (90 chars) : `HTTPException` message
- **Ligne 204** (96 chars) : return `PredictResponse(...)`

### P03 — Ligne trop longue dans `session_state.py`
- **Ligne 441** (125 chars) : signature de `generate_recap_table()` trop longue
- **Ligne 466** (102 chars) : appel à `reference_loader.get_label_for_code()`

---

## 📦 Imports — 10 problèmes

### P04 — Import hors du bloc principal (E402)
**Fichier** : [briefml/ui/app.py:90](briefml/ui/app.py#L90)
**Détail** : `import importlib` placé après du code (contournement pour noms de fichiers numériques)
```python
# Ligne 90 — import positionné après 89 lignes de code
import importlib
```

### P05 — `ConnectionError` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_polish.py:12](tests/integration/test_polish.py#L12)
```python
from requests.exceptions import Timeout, ConnectionError  # ConnectionError inutilisé
```

### P06 — `streamlit` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_us01_reset.py:16](tests/integration/test_us01_reset.py#L16)
```python
import streamlit as st  # inutilisé
```

### P07 — `reference_loader` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_us01_reset.py:20](tests/integration/test_us01_reset.py#L20)
```python
from briefml.ui.lib import session_state, reference_loader  # reference_loader inutilisé
```

### P08 — `session_state` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_us03_dropdown_display.py:11](tests/integration/test_us03_dropdown_display.py#L11)
```python
from briefml.ui.lib import reference_loader, session_state  # session_state inutilisé
```

### P09 — `session_state` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_us05_validation.py:11](tests/integration/test_us05_validation.py#L11)
```python
from briefml.ui.lib import session_state, validation  # session_state inutilisé
```

### P10 — `pytest` importé mais inutilisé (F401)
**Fichier** : [tests/integration/test_us07_prediction.py:10](tests/integration/test_us07_prediction.py#L10)
```python
import pytest  # inutilisé (aucun decorator @pytest.mark)
```

### P11 — `json` importé mais inutilisé (F401)
**Fichier** : [tests/unit/test_api_client.py:11](tests/unit/test_api_client.py#L11)
```python
import json  # inutilisé
```

### P12 — `pytest` importé mais inutilisé (F401)
**Fichier** : [tests/unit/test_api_client.py:14](tests/unit/test_api_client.py#L14)
```python
import pytest  # inutilisé
```

### P13 — `pytest` importé mais inutilisé (F401)
**Fichier** : [tests/unit/test_validation.py:10](tests/unit/test_validation.py#L10)
```python
import pytest  # inutilisé
```

---

## 🏷️ Types — 8 problèmes (Pyright)

### P14 — Type mismatch : `List[str]` → `Axes | None`
**Fichier** : [briefml/api/predictor.py:114](briefml/api/predictor.py#L114)
**Détail** : Un `list[str]` est passé là où Pandas attend `Axes | None` pour le paramètre `columns`

### P15 — `.astype()` inaccessible sur types union (float | Number | NAType | NaTType | Timestamp | Timedelta)
**Fichier** : [briefml/api/predictor.py:138](briefml/api/predictor.py#L138)
**Détail** : Appel `.astype()` sur une valeur dont le type est trop large — Pyright ne peut pas garantir que `.astype` existe sur tous les types possibles

### P16 — Expressions de type invalides dans `models.py` (Pydantic)
**Fichier** : [briefml/ui/lib/models.py:27–76](briefml/ui/lib/models.py#L27)
**Détail** : 14 erreurs Pyright sur les annotations de champs Pydantic (`int` utilisé comme expression de type là où Pyright attend une annotation de type littéral). Problème connu de compatibilité Pyright/Pydantic v2.
```
models.py:27 - Type of "int" could not be determined because it refers to itself
models.py:27 - Variable not allowed in type expression
... (x14)
```

### P17 — `.get()` inaccessible sur `list[dict[str, Any]]`
**Fichier** : [briefml/ui/lib/reference_loader.py:196](briefml/ui/lib/reference_loader.py#L196)
**Détail** : La variable est typée comme `list[dict]` mais `.get()` est appelé dessus comme si c'était un `dict` simple

### P18 — Type mismatch pour paramètre `columns` de `pd.DataFrame`
**Fichier** : [briefml/ui/lib/session_state.py:250](briefml/ui/lib/session_state.py#L250)
**Détail** : `list[str]` passé comme `columns` là où Pyright attend `Axes | None`

---

## 📝 Documentation — 6 problèmes

### P19 — `load_model_and_meta()` sans docstring
**Fichier** : [briefml/api/predictor.py:71](briefml/api/predictor.py#L71)
**Détail** : Fonction critique (charge le modèle CatBoost) sans description, sans doc des paramètres/retours

### P20 — `normalize_input()` sans docstring
**Fichier** : [briefml/api/predictor.py:96](briefml/api/predictor.py#L96)
**Détail** : Fonction de prétraitement ML sans description du comportement (casting, gestion des manquants)

### P21 — `_startup()` sans docstring
**Fichier** : [briefml/api/predictor.py:164](briefml/api/predictor.py#L164)
**Détail** : Lifecycle hook FastAPI sans explication

### P22 — `health()` sans docstring
**Fichier** : [briefml/api/predictor.py:170](briefml/api/predictor.py#L170)
**Détail** : Endpoint `/health` sans description de la réponse retournée

### P23 — `predict()` sans docstring
**Fichier** : [briefml/api/predictor.py:193](briefml/api/predictor.py#L193)
**Détail** : Endpoint principal de l'API sans description complète du format d'entrée/sortie

### P24 — Classe `ModelStore` (méthode `load()`) sans docstring
**Fichier** : [briefml/api/predictor.py:52](briefml/api/predictor.py#L52)
**Détail** : Méthode de chargement du modèle sans documentation

---

## 🔒 Sécurité — 2 problèmes

### P25 — Credentials réels dans `.env` commités historiquement
**Fichier** : `.env`
**Détail** : Le fichier `.env` contient des vraies valeurs (`POSTGRES_PASSWORD=max`, `POSTGRES_USER=max`). Bien qu'exclu du `.gitignore` actuel, il a été commité dans l'historique Git (`git log -- .env` confirme des commits antérieurs).
**Risque** : Credentials exposés si le repo est public ou si l'historique est partagé
**Correction** : `git filter-branch` ou `git-filter-repo` pour purger l'historique, puis rotation des mots de passe

### P26 — Aucune validation du format de l'URL API (`API_URL`)
**Fichier** : [briefml/ui/lib/api_client.py:201](briefml/ui/lib/api_client.py#L201)
**Détail** : La variable d'environnement `API_URL` est utilisée sans validation de format. Une valeur malformée peut entraîner des erreurs silencieuses ou des comportements inattendus.

> **Note Bandit** : Aucune vulnérabilité critique détectée (`bandit -r briefml/` → 0 issues). Le code ne contient pas de secrets en dur, pas de `eval()`, pas de `shell=True`.

---

## ♻️ Code mort — 2 problèmes

### P27 — Variable `response` assignée mais jamais utilisée (F841)
**Fichier** : [tests/integration/test_api_contract.py:54](tests/integration/test_api_contract.py#L54)
```python
response = requests.get(f"{API_URL}/", timeout=5)  # response jamais utilisé après
assert True, "API is reachable"  # assert inutile — toujours True
```

### P28 — `assert True` — assertion inutile
**Fichier** : [tests/integration/test_api_contract.py:56](tests/integration/test_api_contract.py#L56)
**Détail** : `assert True` ne teste rien. Le test ne vérifie pas réellement la réponse HTTP.

---

## ✅ Points positifs

- **Bandit** : 0 vulnérabilité de sécurité statique dans le code source (`briefml/`)
- **Tests unitaires** : 38/38 passent ✅
- **`.env` exclu du `.gitignore`** actuel ✅
- **`.env.example`** fourni comme template ✅
- **Annotations de types** présentes sur la majorité des fonctions publiques ✅

---

## Priorisation des corrections

| Priorité | Problèmes | Action |
|----------|-----------|--------|
| 🔴 Critique | P25 (secrets historique git) | Purger l'historique git |
| 🟠 Haute | P01 (formatage 30 fichiers) | `ruff format .` |
| 🟠 Haute | P04–P13 (imports inutilisés) | `ruff check --fix .` |
| 🟡 Moyenne | P14–P18 (types Pyright) | Corrections manuelles |
| 🟡 Moyenne | P19–P24 (docstrings) | Ajout docstrings Google style |
| 🟢 Basse | P27–P28 (code mort) | Suppression/correction |
