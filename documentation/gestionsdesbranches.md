# Gestion des branches — Questions de réflexion

## 1. Pourquoi protéger les branches ?

La protection des branches empêche toute modification directe sans validation préalable (PR, CI, approbation).

**Sans protection**, n'importe qui pourrait :
- pusher du code non testé directement sur `main` ou `develop`,
- introduire des régressions en production sans revue,
- écraser accidentellement le travail d'un autre développeur,
- bypasser les vérifications automatiques (lint, tests).

La protection garantit que seul du code validé (CI verte + approbation) intègre les branches principales.

---

## 2. Pourquoi Conventional Commits ?

### Avantages pour l'équipe
- **Lisibilité** : l'historique git devient un journal structuré et compréhensible par tous.
- **Collaboration** : chaque commit communique clairement son intention (`feat`, `fix`, `chore`...).
- **Revue de code** : les PR sont plus faciles à évaluer quand le type de changement est explicite.

### Avantages pour le versionnage automatique
- Les outils comme **semantic-release** analysent les types de commits pour déterminer automatiquement la prochaine version :
  - `fix` → bump PATCH (1.0.0 → 1.0.1)
  - `feat` → bump MINOR (1.0.0 → 1.1.0)
  - `feat!` / `BREAKING CHANGE` → bump MAJOR (1.0.0 → 2.0.0)
- Le **changelog** est généré automatiquement à partir des messages de commits.
- Zéro décision manuelle sur le numéro de version : c'est le code qui décide.

---

## 3. Différence entre `develop` et `main`

| | `develop` | `main` |
|---|---|---|
| Rôle | Branche d'intégration continue | Branche de production |
| Stabilité | Code en cours de validation | Code stable et releasé |
| Accès | PR depuis feature branches | PR depuis develop uniquement |
| Déclencheur | Merge de features | Release officielle |

### Quand merger dans `develop` ?
Quand une feature branch est terminée, testée et que la CI passe. C'est l'intégration quotidienne du travail de l'équipe.

### Quand merger dans `main` ?
Uniquement lors d'une **release** : quand `develop` est stable et qu'on veut publier une nouvelle version en production. C'est semantic-release qui déclenche automatiquement ce processus.
