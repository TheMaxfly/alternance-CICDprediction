# Rapport de résolution des incidents - API FastAPI (exercice CI/CD)

## Contexte
Objectif: démarrer l'API `FastAPI` localement via `uv run fastapi dev app/main.py`.

Pendant le diagnostic, plusieurs erreurs successives ont été rencontrées.
Elles sont cohérentes avec un exercice CI/CD comportant des pièges de configuration volontairement introduits.

## Incident 1 - `DATABASE_URL` à `None` au démarrage

### Symptôme
Crash au boot avec:
- `sqlalchemy.exc.ArgumentError: Expected string or URL object, got None`

### Cause racine
`DATABASE_URL` était lu via `os.getenv("DATABASE_URL")`, mais le fichier `.env` n'était pas chargé avant la création de l'engine SQLAlchemy.

### Correction appliquée
- Chargement explicite de l'environnement avec `python-dotenv`.
- Ajout d'un garde-fou qui lève une erreur lisible si `DATABASE_URL` est absent.

### Fichier modifié
- `app/database.py`

## Incident 2 - Hôte `db` introuvable hors Docker

### Symptôme
Après correction 1, nouveau crash:
- `could not translate host name "db" to address`

### Cause racine
La valeur `.env` utilisait `db` comme host PostgreSQL.
`db` est résolu uniquement sur le réseau Docker Compose, pas lors d'un lancement local direct.

### Correction appliquée
- Séparation des URLs:
  - `DATABASE_URL` pour exécution locale (`localhost`).
  - `DATABASE_URL_DOCKER` pour exécution en conteneur (`db`).
- Injection de la variable Docker dédiée dans `docker-compose.yml`.

### Fichiers modifiés
- `.env`
- `.env.example`
- `docker-compose.yml`

## Incident 3 - Échec d'authentification PostgreSQL local

### Symptôme
Nouveau crash:
- `password authentication failed for user "postgres"` sur `localhost:5432`

### Cause racine
Collision probable avec une instance PostgreSQL locale déjà présente sur le port `5432`, avec des credentials différents de `postgres/postgres`.

### Correction appliquée
- Changement du mapping du conteneur DB vers `5433:5432`.
- Mise à jour des variables locales pour pointer `localhost:5433`.

### Fichiers modifiés
- `docker-compose.yml`
- `.env`
- `.env.example`

## Incident 4 - Robustesse du chargement `.env`

### Symptôme
Comportement de chargement `.env` non fiable selon le contexte d'exécution.

### Cause racine
Auto-détection implicite du chemin `.env` pouvant varier selon le point d'entrée.

### Correction appliquée
- Utilisation d'un chemin explicite vers la racine projet:
  - `PROJECT_ROOT = Path(__file__).resolve().parents[1]`
  - `load_dotenv(dotenv_path=PROJECT_ROOT / ".env")`

### Fichier modifié
- `app/database.py`

## Incident 5 - Avertissement Docker Compose

### Symptôme
Avertissement:
- `the attribute 'version' is obsolete`

### Cause racine
Clé `version` devenue obsolète dans la syntaxe Compose moderne.

### Correction appliquée
- Suppression de la ligne `version: '3.8'`.

### Fichier modifié
- `docker-compose.yml`

## Vérifications réalisées
- Import applicatif validé: `import app.main` (sans crash de config).
- Service DB Docker lancé et healthy.
- API lancée avec succès.
- Message de santé fonctionnel (retour attendu: API opérationnelle, ex. `Items CRUD API` sur `/`).

## Fichiers impactés (résumé)
- `app/database.py`
- `docker-compose.yml`
- `.env` (local, non versionné)
- `.env.example`

## Conclusion
Le démarrage de l'API est désormais fonctionnel.
Les erreurs rencontrées sont typiques d'un scénario de test CI/CD:
- gestion d'environnement incomplète,
- divergence local vs Docker,
- conflit de port/service local,
- robustesse de bootstrap applicatif.

Ces corrections stabilisent le run local et la cohérence avec l'environnement conteneurisé.
