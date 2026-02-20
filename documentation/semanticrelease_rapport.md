# semanticrelease_rapport.md — SemVer, Conventional Commits & Python Semantic Release (PSR)

**Date :** 2026-02-15 (Europe/Paris)
**Public cible :** Data Analyste / Développeur IA / Data Engineer
**Objectif :** Documenter les concepts **SemVer** (versionnage sémantique), **Conventional Commits** (commits conventionnels) et expliquer le fonctionnement de **Python Semantic Release (PSR)** : configuration, génération du CHANGELOG, et création de releases GitHub.

---

## Acronymes (développés dès le début)

- **API** : *Application Programming Interface* — interface logicielle (contrat d’utilisation d’un module/service).
- **CI/CD** : *Continuous Integration / Continuous Delivery (ou Deployment)* — intégration continue + livraison/déploiement continu.
- **CLI** : *Command Line Interface* — interface en ligne de commande.
- **IaC** : *Infrastructure as Code* — infrastructure décrite et gérée par du code (Terraform, Pulumi…).
- **PEP** : *Python Enhancement Proposal* — standard/proposition officielle Python.
- **PSR** : *Python Semantic Release* — outil d’automatisation de releases pour projets Python.
- **RFC 2119** : *Request for Comments* — standard définissant la signification de MUST/SHOULD/MAY, etc.
- **SCA** : *Software Composition Analysis* — analyse des dépendances (vulnérabilités, licences).
- **SemVer** : *Semantic Versioning* — versionnage sémantique (MAJOR.MINOR.PATCH).
- **VCS** : *Version Control System* — système de gestion de versions (Git, etc.).

---

## 1) Qu’est-ce que le versionnage sémantique (SemVer) ?

### 1.1 Définition et intention
Le **versionnage sémantique (SemVer)** est une convention qui donne un **sens** aux numéros de version : on peut déduire la **nature** et la **gravité** des changements d’une version à l’autre (correctif, nouvelle fonctionnalité compatible, rupture).
La spécification SemVer formalise cette convention et sert de base à de nombreux outils d’automatisation (release notes, bump de version, gestion de compatibilité).

**Référence :**
- https://semver.org/ (spec officielle)
- https://semver.org/lang/fr/spec/v2.0.0.html (traduction FR)

---

## 2) Format MAJOR.MINOR.PATCH

### 2.1 Règle générale
Une version SemVer suit la forme :

- **MAJOR.MINOR.PATCH**
  Exemple : `2.4.1`

### 2.2 Quand bumper chaque niveau ?

#### 2.2.1 Bump MAJOR (rupture de compatibilité)
On incrémente **MAJOR** lorsqu’on introduit des **changements incompatibles** avec les consommateurs (API/librairie/service/contrat).
Exemples “Data/IA” :
- suppression/renommage d’un endpoint, d’un paramètre, d’un schéma attendu,
- changement de format de sortie (colonnes, types) **sans compatibilité**,
- modification d’une signature de fonction publique utilisée par d’autres dépôts.

#### 2.2.2 Bump MINOR (ajout compatible)
On incrémente **MINOR** lorsqu’on ajoute une fonctionnalité de manière **rétrocompatible**.
Exemples “Data/IA” :
- nouveau connecteur source, nouveau mode d’exécution, nouveau champ optionnel,
- ajout d’une route API sans casser les routes existantes,
- ajout de colonnes non-breaking (si consommateurs tolèrent des colonnes supplémentaires).

#### 2.2.3 Bump PATCH (correctif compatible)
On incrémente **PATCH** lorsqu’on corrige un bug **sans casser** l’API/le contrat.
Exemples “Data/IA” :
- correction d’un calcul, d’un filtre, d’un parsing,
- correction d’un bug de performance/cas limite **sans modifier** le contrat public.

**Référence (règles résumées) :** https://semver.org/

---

## 3) Qu’est-ce que Conventional Commits ?

### 3.1 Définition
**Conventional Commits** est une spécification qui normalise la forme des messages de commit afin qu’ils soient :
- lisibles pour les humains,
- **parsables** par des outils automatiques (génération de changelog, bump de version, release automatisée).

La spécification s’articule explicitement avec SemVer : **feat** → MINOR, **fix** → PATCH, et **BREAKING CHANGE** → MAJOR.

**Référence :** https://www.conventionalcommits.org/fr/v1.0.0/

---

## 4) Format des messages (Conventional Commits)

### 4.1 Format canonique
Le format attendu est :

```
<type>[scope optionnel][! optionnel]: <description>

[body optionnel]

[footer optionnel]
```

- **type** : catégorie de changement (feat, fix, docs…)
- **scope** (facultatif) : zone concernée (api, ingestion, db, ui…)
- **!** (facultatif) : indique un breaking change directement dans l’en-tête
- **description** : courte description (impératif présent recommandé)
- **footer** : peut contenir `BREAKING CHANGE:` et/ou des références de tickets

**Référence :** https://www.conventionalcommits.org/fr/v1.0.0/

### 4.2 Exemples (style “industrie”)
- `feat: add email notifications on new direct messages`
- `fix(api): handle null payload in checksum calculation`
- `feat(api)!: remove deprecated status endpoint`
- `chore(ci): update GitHub Actions runner to ubuntu-24.04`

---

## 5) Types de commits (feat, fix, etc.)

### 5.1 Types minimaux “SemVer-aware”
La spécification implique une interprétation SemVer automatique pour :
- **feat** : nouvelle fonctionnalité (corrélé MINOR)
- **fix** : correction de bug (corrélé PATCH)
- **BREAKING CHANGE** : rupture (corrélé MAJOR)

Les autres types sont autorisés (docs, test, perf, refactor, build, chore, ci…), et peuvent être utilisés par l’équipe, mais **n’impliquent pas** automatiquement un bump SemVer (sauf s’ils contiennent un breaking change).

**Référence :** https://www.conventionalcommits.org/fr/v1.0.0/

### 5.2 Indication de rupture (breaking change)
Un breaking change peut être signalé de 2 façons :

1) Via un `!` dans l’en-tête
   Exemple : `feat(api)!: remove status endpoint`

2) Via un footer en majuscules
   Exemple :
   ```
   feat: change config inheritance behavior

   BREAKING CHANGE: `extends` is now used for extending configs.
   ```

---

## 6) Impact sur le versionnage (lien SemVer ↔ Conventional Commits)

### 6.1 Règle de mapping standard
Dans une automatisation de release basée sur Conventional Commits :

- présence d’un **BREAKING CHANGE** → bump **MAJOR**
- sinon présence d’au moins un **feat** → bump **MINOR**
- sinon présence d’au moins un **fix** → bump **PATCH**
- sinon → généralement **pas de bump** (ou politique d’équipe)

**Références :**
- https://semver.org/
- https://www.conventionalcommits.org/fr/v1.0.0/

---

## 7) Comment Python Semantic Release (PSR) fonctionne ?

### 7.1 Principe général
**Python Semantic Release (PSR)** automatise le processus de release en s’appuyant sur :
1) l’analyse des messages de commit (ex. Conventional Commits),
2) le calcul de la **prochaine version SemVer**,
3) la mise à jour (“bump”) de la version dans les fichiers de projet,
4) la génération/mise à jour du **CHANGELOG**,
5) la création d’un **tag Git** et (optionnellement) d’une **release** sur le VCS distant (ex. GitHub).

PSR est conçu pour fonctionner en **CI/CD**, mais peut aussi être exécuté localement (mode `--noop`) pour valider la configuration.

**Référence documentation PSR :**
- https://python-semantic-release.readthedocs.io/
- https://github.com/python-semantic-release/python-semantic-release

---

## 8) Configuration dans `pyproject.toml`

### 8.1 Emplacement de configuration
Par défaut, PSR lit la configuration dans :

- `pyproject.toml` → table `[tool.semantic_release]`

PSR supporte aussi d’autres fichiers via `-c/--config` (TOML/JSON).

**Référence :** https://python-semantic-release.readthedocs.io/

### 8.2 Configuration minimale recommandée (exemple)
Objectif : utiliser Conventional Commits, mettre à jour la version dans `project.version`, générer un changelog Markdown, et construire l’artefact.

```toml
[project]
name = "my-package"
version = "0.0.0"

[tool.semantic_release]
commit_parser = "conventional"
version_toml = ["pyproject.toml:project.version"]
changelog_file = "CHANGELOG.md"
build_command = "python -m build --sdist --wheel ."
```

> **Remarques pratiques (Data/IA)**
> - Si votre projet est une **lib interne**, `build_command` est pertinent (wheel/sdist).
> - Si votre projet est une **application** (pipeline/service), la release peut plutôt produire une **image Docker** (PSR pilote la version/tag, le pipeline construit/publie l’image).

**Références PSR :**
- Configuration : https://python-semantic-release.readthedocs.io/en/latest/configuration/configuration.html

---

## 9) Génération du CHANGELOG

### 9.1 Principe
Avant de créer une release, PSR génère (ou met à jour) un **CHANGELOG** à partir des commits (filtrage, sections, format). Le changelog est configurable (fichier, format md/rst, templates).

**Référence :**
- https://python-semantic-release.readthedocs.io/en/latest/configuration/configuration.html

### 9.2 Bonnes pratiques
- Conserver `CHANGELOG.md` **dans le dépôt** (traçabilité).
- Filtrer les commits “bruit” (chore/ci/style/test) si votre politique vise des notes orientées “produit”.
- Préserver les “BREAKING CHANGE” dans une section dédiée (impacts utilisateurs).

---

## 10) Création des releases GitHub

### 10.1 Fonctionnement “CI-friendly”
PSR peut :
- créer un tag,
- pousser les commits de bump de version,
- créer une **release GitHub** (release notes, assets) si un token et les permissions adéquates sont présents.

Références :
- GitHub repo PSR : https://github.com/python-semantic-release/python-semantic-release
- Marketplace : https://github.com/marketplace/actions/python-semantic-release

### 10.2 Exemple minimal (conceptuel) en GitHub Actions
> Exemple “générique” à adapter à votre repo, règles de branches, et secrets.

```yaml
name: release

on:
  push:
    branches: [ "main" ]

jobs:
  release:
    runs-on: ubuntu-24.04
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install PSR
        run: python -m pip install python-semantic-release

      - name: Run semantic release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release version --vcs-release
```

**Points d’attention**
- `fetch-depth: 0` : requis pour l’historique et les tags.
- `permissions: contents: write` : requis pour pousser tags/commits et créer la release.
- Selon l’organisation, un **PAT** (Personal Access Token) peut être nécessaire si `GITHUB_TOKEN` est restreint.

---

## 11) Synthèse “niveau Data Engineer / Développeur IA”

- **SemVer** fournit le langage commun des versions : MAJOR/MINOR/PATCH.
- **Conventional Commits** rend l’historique Git “machine-readable” et déclenche l’automatisation.
- **PSR** industrialise le tout : détecte le bump, met à jour la version, génère un changelog, crée un tag, et peut publier une release GitHub.

Ce triptyque est particulièrement utile en Data/IA pour :
- sécuriser la diffusion d’un SDK interne (clients DB, connecteurs, libs de features),
- stabiliser les pipelines (contrats de schémas),
- accélérer les cycles de livraison avec une gouvernance claire.

---

## Bibliographie (liens officiels)

- SemVer 2.0.0 : https://semver.org/ (FR : https://semver.org/lang/fr/spec/v2.0.0.html)
- Conventional Commits 1.0.0 : https://www.conventionalcommits.org/fr/v1.0.0/
- Python Semantic Release (docs) : https://python-semantic-release.readthedocs.io/
- Python Semantic Release (GitHub) : https://github.com/python-semantic-release/python-semantic-release
- GitHub Marketplace (PSR Action) : https://github.com/marketplace/actions/python-semantic-release
