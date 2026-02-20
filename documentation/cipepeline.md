# CI Pipeline — Questions de réflexion

## 1. Pourquoi plusieurs jobs séparés ?

### Avantages du parallélisme
Les 4 jobs (lint, typecheck, security, tests) s'exécutent **simultanément** sur GitHub Actions. Sans séparation, ils tourneraient en séquence et le temps total serait la somme de chacun. Avec des jobs parallèles, le temps total est celui du job le plus long.

Exemple concret :
```
Sans parallélisme : lint (30s) + typecheck (45s) + security (60s) + tests (90s) = 225s
Avec parallélisme : max(30s, 45s, 60s, 90s) = 90s
```

### Facilité de débogage
Chaque job a une responsabilité unique. Quand la CI échoue, on sait immédiatement **quelle catégorie** est en cause sans lire toute la sortie d'un seul job monolithique :
- ❌ lint → problème de formatage ou de style
- ❌ typecheck → annotation de type manquante ou incorrecte
- ❌ security → vulnérabilité détectée
- ❌ tests → régression fonctionnelle

---

## 2. Que faire si la CI échoue ?

### Comment lire les logs
1. Aller sur **GitHub → Actions → le run en question**
2. Cliquer sur le job en rouge
3. Développer l'étape en échec (triangle rouge)
4. Lire le message d'erreur : il indique le fichier, la ligne et la règle violée

Les erreurs sont toujours de la forme :
```
fichier.py:ligne: error: description [code-règle]
```

### Comment reproduire localement
Avant de pusher, lancer les mêmes commandes qu'en CI :

```bash
# Lint
uv run ruff check .
uv run ruff format --check .

# Typecheck
uv run mypy app/

# Security
uv run bandit -r app/
uv run safety scan --no-telemetry

# Tests
uv run pytest --cov=app --cov-report=term-missing
```

Reproduire localement évite des allers-retours inutiles avec GitHub Actions et accélère le cycle de correction.

---

## 3. Faut-il tout corriger d'un coup ?

Non. Le brief recommande des **PR par catégorie** et c'est la bonne pratique.

### Avantages des petites PR
- Chaque PR a un **objectif clair** (ex. `fix/add-type-annotations`)
- Plus facile à annuler (`git revert`) si une correction introduit une régression
- La CI donne un feedback précis sur un périmètre limité
- L'historique git reste lisible : chaque commit raconte une histoire cohérente

### Facilité de review
- Un reviewer peut valider une PR de 50 lignes en quelques minutes
- Une PR de 500 lignes mélangeant lint + types + tests + sécurité est difficile à relire et à approuver avec confiance
- Les petites PR réduisent le risque d'erreur de review et accélèrent les merges
