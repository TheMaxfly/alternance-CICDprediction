# Data Assets

Ce dossier contient les données nécessaires à l'application.

## Politique de versionnement

- Les petits fichiers de référence (ex: `ref_options.json`) sont commités directement.
- Les fichiers lourds (`.csv`, `.parquet`) sont suivis via Git LFS.

## Mise en place Git LFS

```bash
git lfs install
git lfs pull
```

## Vérification

```bash
git lfs ls-files
```

Si un fichier attendu est absent sur une machine, vérifier d'abord que Git LFS est installé et que `git lfs pull` a été exécuté.
