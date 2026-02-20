# VEILLE_UV.md — Mission 2 : Maîtriser uv (1h)
**Version :** 1.0
**Date :** 2026-02-15 (Europe/Paris)
**Profil visé :** Data Analyste / Data Engineer / Développeur IA
**Objectif pédagogique :** Comprendre **uv**, ses différences avec pip/poetry/pipenv, sa relation à `pyproject.toml` (dépendances, groupes, packaging), et sa mise en œuvre dans **GitHub Actions** (installation + cache) avec de bonnes pratiques “industrie”.

---

## Acronymes (développés dès le début)

- **CI/CD** : *Continuous Integration / Continuous Delivery (ou Deployment)* — intégration continue + livraison/déploiement continu.
- **CLI** : *Command Line Interface* — interface en ligne de commande.
- **PEP** : *Python Enhancement Proposal* — standard/proposition officielle de l’écosystème Python.
- **PEP 517** : standard du build Python (définit l’interface “build backend”).
- **PEP 621** : standard des métadonnées projet dans `pyproject.toml`.
- **VCS** : *Version Control System* — système de gestion de versions (ex. Git).
- **Wheel** : paquet Python préconstruit (`.whl`) généralement rapide à installer.
- **sdist** : distribution source (`.tar.gz`) nécessitant parfois un build lors de l’installation.

---

## 0) Ressources (obligatoires + documentation officielle)

### Ressources obligatoires
- **Documentation uv (Astral)** : installation + concepts projets + dépendances + cache. (https://docs.astral.sh/uv/getting-started/installation/)
- **uv — GitHub Integration** (guide officiel “Using uv in GitHub Actions”). (https://docs.astral.sh/uv/guides/integration/github/)
- **uv — Build Backend** (documentation officielle `uv_build`). (https://docs.astral.sh/uv/concepts/build-backend/)
- **uv Tutorial (vidéo)** : prise en main (workflows, commandes). *(Référence vidéo fournie dans le brief — à ajouter dans votre bibliographie interne si vous devez tracer l’URL exacte utilisée.)*

### Références complémentaires (officielles)
- **Action GitHub officielle** `astral-sh/setup-uv` (README + options). (https://github.com/astral-sh/setup-uv)
- **Settings uv** (positionnement de `tool.uv.dev-dependencies` vs `dependency-groups`). (https://docs.astral.sh/uv/reference/settings/)

---

## 1) Qu’est-ce que uv ?

### 1.1 Définition (orientée production/CI)
**uv** est un outil moderne de gestion d’environnement et de dépendances Python, conçu pour offrir une expérience “projet” complète : installation et synchronisation des dépendances, cache, intégration CI, et prise en charge du packaging/build via un backend dédié. La documentation uv décrit explicitement ses concepts de projets (packaging, configuration) et ses mécanismes de cache et d’intégration CI.

### 1.2 Pourquoi c’est stratégique en Data/IA
Les projets Data/IA cumulent souvent :
- des dépendances lourdes (scientifique/ML),
- des contraintes de versions strictes,
- un besoin élevé de reproductibilité (dev ↔ CI ↔ prod),
- des pipelines/ETL où une dérive d’environnement peut provoquer des erreurs coûteuses.

uv répond à ce besoin via :
- **synchronisation reproductible** des environnements (concept “project sync”),
- **cache** pour accélérer les installations,
- et une **intégration GitHub Actions** documentée.

---

## 2) En quoi uv est différent de pip / poetry / pipenv ?

### 2.1 Différence avec pip (approche “outil de base”)
- **pip** est un installateur de paquets, orienté installation, mais ne fournit pas à lui seul un cadre “projet” complet (workflow projet, cache CI structuré, recommandations d’intégration, etc.).
- uv propose un **cadre projet** plus explicite : configuration projet, packaging (si nécessaire), cache, guide CI, et une logique de synchronisation d’environnement.

### 2.2 Différence avec Poetry / Pipenv (approche “gestion de projet”)
Poetry/Pipenv adressent la gestion de projet (dépendances, lock, etc.) ; uv se différencie surtout par :
- une documentation forte sur **l’intégration CI** (GitHub Actions + cache + prune),
- un backend de build (`uv_build`) documenté,
- et une structuration moderne des dépendances de développement via **dependency groups** (standardisation recommandée).

### 2.3 Différence structurante en contexte équipe
Dans une équipe Data/IA, l’enjeu est moins “quel outil est le plus populaire” que :
- **reproduire** l’environnement à l’identique,
- **accélérer** la CI (cache),
- **réduire** la variabilité (mêmes commandes, mêmes groupes),
- et industrialiser packaging/déploiement (wheel ou image).

uv fournit un corpus officiel de pratiques CI (cache + prune, patterns), utile pour standardiser.

---

## 3) Quels sont les avantages de uv ?

### 3.1 Avantages techniques (niveau professionnel)
1. **Reproductibilité** : capacité à reconstruire un environnement cohérent via synchronisation (et lockfile), indispensable en CI/CD.
2. **Performance CI** : un **cache** explicitement documenté (et recommandé), particulièrement utile pour stacks Data/IA lourdes.
3. **Gouvernance des dépendances** : séparation claire entre dépendances publiées et dépendances de développement via **dependency groups** (approche recommandée).
4. **Packaging intégré** : possibilité d’utiliser `uv_build` pour des projets pure Python (wheels/sdist), facilitant la distribution interne.
5. **Intégration GitHub Actions “ready-to-use”** : guide officiel + action officielle pour installer uv + support du cache.

### 3.2 Avantages organisationnels (Data/IA)
- Moins d’écarts entre postes : même structure `pyproject.toml` + mêmes groupes.
- CI plus rapide → feedback plus court → meilleure productivité.
- Packaging et release plus propres (artefacts versionnés, traçabilité).

---

## 4) Comment uv fonctionne avec `pyproject.toml` ?

### 4.1 Structure du fichier (rappel PEP 621 + organisation uv)
`pyproject.toml` centralise :
- les métadonnées projet (`[project]`, PEP 621),
- les dépendances d’exécution,
- les dépendances de développement (via dependency groups),
- et éventuellement le système de build (`[build-system]`).

uv documente des éléments clés sur la configuration projet et le packaging (quand un projet doit être “packagé” vs simple script/application).

### 4.2 Gestion des dépendances (séparées par sections)

#### 4.2.1 Dépendances “runtime” (publiées)
- `project.dependencies` : dépendances nécessaires au fonctionnement du projet.

#### 4.2.2 Dépendances optionnelles (extras)
- `project.optional-dependencies` : variantes optionnelles (ex. `ml`, `gpu`, etc.) si vous publiez un package.

#### 4.2.3 Dépendances de développement (groupes)
- `dependency-groups.dev`, `dependency-groups.test`, `dependency-groups.lint`, etc.
uv indique que l’usage de `tool.uv.dev-dependencies` **n’est plus recommandé** et qu’il faut préférer `dependency-groups.dev` (standardisé). La doc précise aussi comment ces champs sont combinés si les deux existent.

> **Recommandation Data/IA**
> - `dev` : notebooks/outils locaux (optionnel)
> - `test` : pytest, fixtures
> - `lint` : ruff, mypy
> - `dq` : Great Expectations / dbt tests (selon stack)
> Résultat : CI plus rapide et images plus légères (on n’installe que ce qui est utile à l’étape).

### 4.3 Exemple `pyproject.toml` (Data/IA : runtime + groupes + packaging)

```toml
[project]
name = "data-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pandas>=2.2",
  "sqlalchemy>=2.0",
  "pyarrow>=15",
]

[dependency-groups]
lint = ["ruff>=0.7", "mypy>=1.10"]
test = ["pytest>=8", "pytest-cov>=5"]
dq = ["great-expectations>=0.18"]

[build-system]
requires = ["uv_build>=0.10.2,<0.11.0"]
build-backend = "uv_build"
```

---

## 4.4 Build backend : rôle et implications (suite)

### 4.4.1 À quoi sert un build backend (rappel PEP 517)
Un **build backend** (standardisé par la **PEP 517**) définit **comment construire** les artefacts de distribution d’un projet Python, notamment :
- une **wheel** (`.whl`) : paquet préconstruit, rapide à installer,
- une **sdist** (`.tar.gz`) : distribution source.

Dans une chaîne **CI/CD**, le build backend devient essentiel dès qu’on veut :
- **packager** une librairie interne (ex. `data-utils`, `feature-store-client`),
- produire un artefact versionné (wheel) pour déploiement/réutilisation,
- standardiser le build (reproductibilité, auditabilité).

> **Implication pratique (Data/IA)**
> - **Application** (ETL/ELT, API, orchestration) : packaging parfois optionnel ; livrable = image Docker / environnement figé.
> - **Bibliothèque réutilisable** : packaging stratégique ; livrable = wheel versionnée.

### 4.4.2 `uv_build` : objectifs, configuration et limites
uv propose un backend officiel **`uv_build`**.

#### Déclaration recommandée dans `pyproject.toml`
```toml
[build-system]
requires = ["uv_build>=0.10.2,<0.11.0"]
build-backend = "uv_build"
```

#### Limitation majeure (Data/IA)
Le backend uv ne supporte actuellement que le **pure Python** ; un backend alternatif est requis pour des modules avec extensions compilées.

**Décision pratique**
- Projet “application data/IA” : `uv_build` optionnel ; privilégier Docker si besoin de runtime homogène.
- Projet “lib interne” : `uv_build` utile pour produire wheels et versions.

### 4.4.3 Interaction avec la CI/CD (artefacts et traçabilité)
Activer le packaging en CI permet :
- d’archiver une **wheel** en artefact CI,
- de publier sur un registre (release GitHub, dépôt interne),
- d’aligner le packaging avec une stratégie de versioning.

**Bonnes pratiques**
- wheel = **artefact de build** (reproductible, versionné, scannable),
- corrélation : **build ⇄ commit ⇄ tag ⇄ changelog**.

---

## 5) Comment utiliser uv dans GitHub Actions ?

### 5.1 Installation (approches recommandées)

#### 5.1.1 Approche A — Action officielle `astral-sh/setup-uv` (recommandée)
Astral propose une action officielle pour installer uv et (optionnellement) persister le cache uv.

Exemple minimal (cache intégré) :
```yaml
- uses: astral-sh/setup-uv@v7
  with:
    enable-cache: true
```

**Pourquoi c’est recommandé**
- installation homogène et maintenue,
- moins de variabilité qu’un bootstrap “pip install uv”,
- configuration plus lisible en CI.

#### 5.1.2 Approche B — Installation via script/gestionnaire
uv documente des méthodes d’installation via installateurs ; cette voie est valable, mais en CI l’action est généralement plus standard.

---

## 5.2 Cache des dépendances (recommandations CI)

### 5.2.1 Pourquoi le cache est critique en Data/IA
Les stacks Data/IA impliquent souvent :
- gros volumes de wheels,
- builds depuis source possibles,
- installations lentes sans cache.

uv indique que le cache est structurel (uv nécessite un cache directory) et recommande de privilégier `--refresh` plutôt que désactiver le cache, car le cache sert la performance et la reproductibilité.

### 5.2.2 Pattern officiel uv + GitHub Actions (cache + prune)
Le guide GitHub officiel propose :
- usage de `astral-sh/setup-uv` avec `enable-cache: true`,
- ou un cache manuel via `actions/cache`,
- et recommande `uv cache prune --ci` pour maîtriser la taille du cache.

---

## 5.3 Recommandations “niveau professionnel” pour GitHub Actions

### 5.3.1 Reproductibilité : `uv sync` en CI
`uv sync` est la commande centrale de synchronisation (environnement aligné sur l’état projet/lock).

**Recommandation d’industrialisation**
- verrouiller les dépendances via lockfile,
- utiliser un mode “gelé” (`--frozen`) en CI lorsque votre politique exige un environnement strictement conforme au lockfile (reproductibilité).

### 5.3.2 Stratégie de cache : clé basée sur `uv.lock`
Un cache efficace doit être invalidé lorsque les dépendances changent :
- clé : hash de `uv.lock`,
- bénéfice : PR sans changement de dépendances → cache réutilisé.

### 5.3.3 Gouvernance : minimiser la surface d’installation (dependency groups)
Application CI :
- installer uniquement `lint` + `test` dans les jobs qualité,
- éviter notebooks, extras GPU, docs si non requis.

---

## 6) Mise en œuvre : workflow GitHub Actions “Data/IA” (uv + cache + sync + tests)

### 6.1 Variante A — `setup-uv` avec cache intégré (simple et maintenable)

```yaml
name: ci-uv

on:
  pull_request:
  push:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv (with cache)
        uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Sync environment
        run: uv sync --all-groups

      - name: Test suite
        run: uv run pytest -q
```

**Points forts**
- lisibilité,
- caching activé,
- standardisation (action officielle).

### 6.2 Variante B — Cache manuel (pattern officiel : `UV_CACHE_DIR` + prune)

```yaml
name: ci-uv-manual-cache

on:
  pull_request:
  push:
    branches: [ "main" ]

jobs:
  test:
    runs-on: ubuntu-24.04
    env:
      UV_CACHE_DIR: /tmp/.uv-cache
    steps:
      - uses: actions/checkout@v4

      - name: Setup uv
        uses: astral-sh/setup-uv@v7

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Restore uv cache
        uses: actions/cache@v4
        with:
          path: /tmp/.uv-cache
          key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}

      - name: Sync environment
        run: uv sync --all-groups

      - name: Run tests
        run: uv run pytest -q

      - name: Prune uv cache (CI)
        run: uv cache prune --ci
```

**Justification**
- contrôle précis de l’emplacement du cache,
- cohérent avec l’approche documentée (cache + prune),
- utile en self-hosted pour éviter croissance illimitée.

---

## 7) Bonnes pratiques spécifiques Data Engineer / Développeur IA

### 7.1 Structurer les dépendances par groupes (dev/test/lint/dq)
Objectif : réduire le temps d’installation et la surface d’attaque en CI.

Exemples :
- `lint` : ruff, mypy
- `test` : pytest, pytest-cov
- `dq` : great-expectations (ou dbt tests selon stack)
- `docs` : mkdocs (si docs auto)

### 7.2 Éviter la dépendance à la production dans la CI
- tests d’intégration DB sur Postgres éphémère (containers),
- DQ sur dataset snapshot/fixture contrôlé,
- pas de secrets prod nécessaires pour valider une PR.

### 7.3 Reproductibilité stricte
- committer `uv.lock`,
- CI “gelée” si nécessaire (`--frozen`),
- pinner `ubuntu-24.04` (limiter surprises de `ubuntu-latest`).

### 7.4 Choisir la stratégie de livrable (packaging vs conteneur)
- **Lib interne** : wheel (build backend) + version SemVer + publication interne.
- **Service/pipeline** : image Docker + scan + tag + release.
- **Notebook-only** : industrialisation recommandée (scripts/package), sinon CI partielle.

---

## 8) Conclusion (synthèse orientée mise en œuvre)

uv est particulièrement pertinent en Data/IA car il combine :
- **cache** et performances utiles sur dépendances lourdes,
- une **intégration GitHub Actions** documentée (cache + prune + action officielle),
- une **structuration moderne** des dépendances via `dependency-groups`,
- et un **backend de build** officiel pour projets pure Python (`uv_build`).

Pour une mise en production “niveau professionnel”, l’adoption uv doit être cadrée par :
1. un `pyproject.toml` structuré (runtime vs groups),
2. un lockfile versionné et une politique de sync reproductible en CI,
3. une stratégie de cache explicite (avec `prune --ci` si besoin),
4. une stratégie de livrables (wheel pour libs internes, Docker pour services/pipelines).
