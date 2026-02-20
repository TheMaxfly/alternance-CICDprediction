# Rapport — MkDocs, GitHub Pages et mkdocstrings

## 1) Comment MkDocs génère de la documentation ?

### Principe
**MkDocs** est un générateur de site **statique** orienté documentation : tu écris tes pages en **Markdown**, et MkDocs les convertit en site web (HTML/CSS/JS).

### Entrées et configuration
Un projet MkDocs repose généralement sur :
- un fichier de configuration `mkdocs.yml`
- un dossier `docs/` qui contient les sources Markdown (ex. `index.md`)

La configuration (dans `mkdocs.yml`) pilote le nom du site, le thème, la navigation et d’autres options. Au minimum, `site_name` est requis.

### Génération (build)
Le build consiste à :
1. lire `mkdocs.yml`
2. parser les fichiers Markdown du dossier `docs/`
3. appliquer le thème
4. produire un dossier de sortie (souvent `site/`) contenant le site statique

> Astuce : `mkdocs serve` lance un serveur local avec rechargement automatique pendant que tu écris.

---

## 2) Comment déployer sur GitHub Pages ?

### Rappel : GitHub Pages
**GitHub Pages** héberge un site statique à partir d’un dépôt GitHub (fichiers HTML/CSS/JS), avec éventuellement un processus de build.

### Option A — Déploiement “MkDocs natif” avec `mkdocs gh-deploy` (simple)
MkDocs fournit une commande dédiée : `mkdocs gh-deploy`.

- Elle build la doc.
- Elle publie ensuite le résultat sur la branche `gh-pages` (en s’appuyant généralement sur `ghp-import`).

Exemple :
```bash
mkdocs build
mkdocs gh-deploy
```

**Avantages**
- Très rapide à mettre en place.
- Courant pour un projet de documentation.

**Points d’attention**
- Il faut que GitHub Pages soit configuré pour publier depuis la branche `gh-pages` (voir Option C).

### Option B — Déploiement via GitHub Actions (recommandé dès que tu veux industrialiser)
Avec GitHub Actions, tu automatises le build et le déploiement à chaque push (ou à chaque merge vers `main`), avec un résultat reproductible.

**Avantages**
- Reproductible (CI/CD).
- Pas besoin de committer les fichiers générés dans ta branche principale.
- Standard en équipe (contrôles via PR).

**Points d’attention**
- Il faut gérer les permissions GitHub Pages (et parfois le cache Python) dans le workflow.
- Selon l’approche, tu peux publier :
  - soit en poussant sur `gh-pages`,
  - soit via le mécanisme “GitHub Pages via Actions” (voir Option C).

### Option C — Réglage “source de publication” côté GitHub Pages
Côté GitHub (Settings → Pages), tu choisis comment Pages publie ton site :
- **Depuis une branche** : typiquement `gh-pages` et le dossier `/` (site généré committé dans `gh-pages`).
- **Via un workflow GitHub Actions** : GitHub Actions build puis déploie l’artefact Pages (pas besoin d’une branche `gh-pages` gérée à la main).

---

## 3) Qu’est-ce que mkdocstrings ?

### Définition
**mkdocstrings** est un plugin “autodoc” pour MkDocs : il génère de la documentation à partir des docstrings (et/ou métadonnées du code) et l’insère dans tes pages Markdown.

### Fonctionnement (idée clé : injection inline)
Au lieu de générer des fichiers Markdown séparés, mkdocstrings permet d’injecter la doc à un endroit précis via une directive.

Exemple (dans une page Markdown) :
```markdown
::: app.main
```

L’identifiant (ici `app.main`) et la configuration sont transmis à un “handler” (Python, etc.) qui extrait et rend la doc.

### Pourquoi l’utiliser ?
- Créer une “API reference” propre sans copier-coller.
- Garder la doc synchronisée avec le code (source of truth = docstrings).
- Alternative moderne à une approche type “Sphinx autodoc”, dans l’écosystème MkDocs.

## Sources (docs officielles)
- MkDocs — Getting started / Configuration / Deploying your docs
- Material for MkDocs — Publishing your site
- GitHub Docs — GitHub Pages (publishing source, quickstart)
- mkdocstrings — Overview
