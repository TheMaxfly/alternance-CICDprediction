# Référentiel d’entrée — Modèle CatBoost (product15_v2 : `time_bucket` à la place de `minute`)

Ce document décrit **les 15 variables** conservées pour le modèle final, avec **leur signification** et **les codes/catégories attendus**.

## Règle de décision

- Le modèle renvoie une probabilité `proba` (0 à 1) d’**accident grave**.
- **Classe prédite** : `grave` si `proba ≥ 0.47`, sinon `non_grave`.

## Variables d’entrée (15)

> Conseil pratique : pour les variables “code BAAC”, saisir le **code** (ex. `lum=1`) ou proposer un menu déroulant avec le libellé.

| Variable | Type attendu | Description |
|---|---|---|
| `dep` | catégorielle (string) | Département (code INSEE/BAAC, ex. `59`, `75`, `2A`, `971`). |
| `lum` | catégorielle (code numérique) | Conditions d’éclairage (luminosité) au moment de l’accident. |
| `atm` | catégorielle (code numérique) | Conditions atmosphériques au moment de l’accident. |
| `catr` | catégorielle (code numérique) | Catégorie de route. |
| `agg` | catégorielle (code numérique) | Agglomération : accident en/hors agglomération. |
| `int` | catégorielle (code numérique) | Type d’intersection. |
| `circ` | catégorielle (code numérique) | Régime de circulation (sens unique, bidirectionnelle, etc.). |
| `col` | catégorielle (code numérique) | Type de collision. |
| `vma_bucket` | catégorielle (string) | Classe de vitesse maximale autorisée (VMA) en km/h (regroupement). |
| `catv_family_4` | catégorielle (string) | Famille de véhicule (regroupement en 4 classes). |
| `manv_mode` | catégorielle (code numérique) | Manœuvre (mode) : manœuvre la plus fréquente parmi les véhicules impliqués (en pratique, saisir la manœuvre du véhicule principal). |
| `driver_age_bucket` | catégorielle (string) | Classe d’âge du conducteur (regroupement). |
| `choc_mode` | catégorielle (code numérique) | Point de choc initial (mode) : point de choc le plus fréquent (en pratique, saisir le point de choc du véhicule principal). |
| `driver_trajet_family` | catégorielle (string) | Famille du trajet conducteur (regroupement robuste des codes `trajet`). |
| `time_bucket` | catégorielle (string) | Tranche horaire dérivée de `hour` (catégories UI simplifiées). |

## Codes et catégories

### `dep` — Département (107 codes observés)

Saisir un code parmi :

```
01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15
16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 2A, 2B
30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44
45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59
60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74
75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89
90, 91, 92, 93, 94, 95, 971, 972, 973, 974, 975, 976, 977, 978, 986
987, 988
```

### `lum` — Conditions d’éclairage

| Code | Libellé |
|---:|---|
| `1` | Plein jour |
| `2` | Crépuscule ou aube |
| `3` | Nuit sans éclairage public |
| `4` | Nuit avec éclairage public non allumé |
| `5` | Nuit avec éclairage public allumé |

> Valeurs manquantes : dans les données brutes, `lum` peut être absent. Dans l’app, prévoir “Non renseigné” si l’utilisateur ne sait pas.

### `atm` — Conditions atmosphériques

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `1` | Normale |
| `2` | Pluie légère |
| `3` | Pluie forte |
| `4` | Neige / grêle |
| `5` | Brouillard / fumée |
| `6` | Vent fort / tempête |
| `7` | Temps éblouissant |
| `8` | Temps couvert |
| `9` | Autre |

### `agg` — Agglomération

| Code | Libellé |
|---:|---|
| `1` | Hors agglomération |
| `2` | En agglomération |

### `catr` — Catégorie de route

| Code | Libellé |
|---:|---|
| `1` | Autoroute |
| `2` | Route nationale |
| `3` | Route départementale |
| `4` | Voie communale |
| `5` | Hors réseau public |
| `6` | Parc de stationnement ouvert à la circulation publique |
| `7` | Routes de métropole urbaine |
| `9` | Autre |

### `int` — Type d’intersection

| Code | Libellé |
|---:|---|
| `1` | Hors intersection |
| `2` | Intersection en X |
| `3` | Intersection en T |
| `4` | Intersection en Y |
| `5` | Intersection à plus de 4 branches |
| `6` | Giratoire |
| `7` | Place |
| `8` | Passage à niveau |
| `9` | Autre intersection |

### `circ` — Régime de circulation

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `1` | Sens unique |
| `2` | Bidirectionnelle |
| `3` | Chaussées séparées |
| `4` | Voies d’affectation variable |

### `col` — Type de collision

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `1` | 2 véhicules - frontale |
| `2` | 2 véhicules - par l’arrière |
| `3` | 2 véhicules - par le côté |
| `4` | 3+ véhicules - en chaîne |
| `5` | 3+ véhicules - collisions multiples |
| `6` | Autre collision |
| `7` | Sans collision |

### `manv_mode` — Manœuvre (code `manv` BAAC)

Dans le dataset, c’est le **mode** (valeur la plus fréquente) des manœuvres des véhicules impliqués. Pour un formulaire utilisateur, on peut demander **la manœuvre du véhicule principal**.

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `0` | Inconnue |
| `1` | Sans changement de direction |
| `2` | Même sens, même file |
| `3` | Entre 2 files |
| `4` | Marche arrière |
| `5` | Contresens |
| `6` | Franchissant TPC |
| `7` | Couloir bus même sens |
| `8` | Couloir bus sens inverse |
| `9` | S’insérant |
| `10` | Demi-tour sur chaussée |
| `11` | Change file gauche |
| `12` | Change file droite |
| `13` | Déporté gauche |
| `14` | Déporté droite |
| `15` | Tournant gauche |
| `16` | Tournant droite |
| `17` | Dépassant gauche |
| `18` | Dépassant droite |
| `19` | Traversant chaussée |
| `20` | Stationnement |
| `21` | Évitement |
| `22` | Ouverture de porte |
| `23` | Arrêté (hors stationnement) |
| `24` | En stationnement (avec occupants) |
| `25` | Circulant sur trottoir |
| `26` | Autres manœuvres |

### `choc_mode` — Point de choc initial (code `choc` BAAC)

Dans le dataset, c’est le **mode** (valeur la plus fréquente) des points de choc initiaux des véhicules impliqués. Pour un formulaire utilisateur, on peut demander **le point de choc du véhicule principal**.

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `0` | Aucun |
| `1` | Avant |
| `2` | Avant droit |
| `3` | Avant gauche |
| `4` | Arrière |
| `5` | Arrière droit |
| `6` | Arrière gauche |
| `7` | Côté droit |
| `8` | Côté gauche |
| `9` | Chocs multiples / tonneaux |

### `driver_trajet_family` — Famille de trajet conducteur

Cette feature regroupe les codes `trajet` sous la forme `trajet_<code>`.

| Code | Libellé |
|---:|---|
| `trajet_1` | Domicile–travail |
| `trajet_2` | Domicile–école |
| `trajet_3` | Courses–achats |
| `trajet_4` | Utilisation professionnelle |
| `trajet_5` | Promenade–loisirs |
| `trajet_9` | Autre |
| `unknown` | Non renseigné / inconnu |

Référence codes BAAC `trajet` (si tu veux aussi l’afficher tel quel) :

| Code | Libellé |
|---:|---|
| `-1` | Non renseigné |
| `0` | Non renseigné |
| `1` | Domicile–travail |
| `2` | Domicile–école |
| `3` | Courses–achats |
| `4` | Utilisation professionnelle |
| `5` | Promenade–loisirs |
| `9` | Autre |

### `driver_age_bucket` — Classe d’âge conducteur

| Code | Libellé |
|---:|---|
| `<18` | Moins de 18 ans |
| `18-24` | 18 à 24 ans |
| `25-34` | 25 à 34 ans |
| `35-44` | 35 à 44 ans |
| `45-54` | 45 à 54 ans |
| `55-64` | 55 à 64 ans |
| `65-74` | 65 à 74 ans |
| `75+` | 75 ans et plus |
| `unknown` | Âge inconnu / non renseigné |

> Remarque : en pratique, tu peux demander l’**âge en années** et convertir en bucket côté code.

### `vma_bucket` — Vitesse maximale autorisée (bucket)

| Code | Libellé |
|---:|---|
| `<=30` | ≤ 30 km/h |
| `31-50` | 31 à 50 km/h |
| `51-80` | 51 à 80 km/h |
| `81-90` | 81 à 90 km/h |
| `91-110` | 91 à 110 km/h |
| `111-130` | 111 à 130 km/h |
| `>130` | > 130 km/h |
| `inconnue` | VMA inconnue / non renseignée |

### `catv_family_4` — Famille de véhicule (4 classes)

| Code | Libellé |
|---:|---|
| `voitures_utilitaires` | Voitures particulières + utilitaires légers (incl. camionnettes). |
| `2rm_3rm` | Deux-roues / trois-roues motorisés (motos, scooters, cyclomoteurs…). |
| `lourds_tc_agri_autres` | Poids lourds + transport en commun + agricoles/spéciaux/autres. |
| `vulnerables` | Usagers/engins vulnérables (ex. vélos, EDPM…) regroupés côté véhicule. |

> Note : ce regroupement dépend du mapping réalisé dans le feature engineering à partir de `catv` (catégorie véhicule BAAC).

### `time_bucket` — Tranche horaire (simplifiée pour l’UI)

Variable **catégorielle** dérivée de l’heure (`hour`) afin d’éviter de demander une heure/minute précises.

| Code | Libellé | Plage |
|---|---|---|
| `night_00_05` | Nuit | 00:00–05:59 |
| `morning_06_11` | Matin | 06:00–11:59 |
| `afternoon_12_17` | Après‑midi | 12:00–17:59 |
| `evening_18_23` | Soir | 18:00–23:59 |
**Exemple** : si l’heure est `05:40`, alors `time_bucket = night_00_05`.


## Conseils d’implémentation (formulaire)

- Utiliser des **menus déroulants** pour les variables codées (lum, atm, catr, agg, int, circ, col, manv_mode, choc_mode).
- Accepter une option “Non renseigné” (souvent `-1` ou `unknown`).
- Pour `time_bucket`, proposer 4 choix simples (Nuit/Matin/Après‑midi/Soir) sans option “Non renseigné”.
