# Data Dictionary — accidents_model_ready.csv

- Granularité : 1 ligne = 1 accident (clé `Num_Acc`)
- Période : 2022–2024
- Cible : `grave` (binaire)

## 1) Dictionnaire des colonnes (80 colonnes)

| Colonne | Type (CSV) | Source | Description | Modalités / domaine |
|---|---|---|---|---|
| `Num_Acc` | int64 | BAAC (clé) | Identifiant unique de l’accident (clé de jointure entre Caractéristiques/Lieux/Véhicules/Usagers). | Unique |
| `grave` | int64 | Feature (cible) | Variable cible binaire : 0 si aucun usager n’est victime (tous indemnes), 1 si au moins un usager est victime (tué / blessé hospitalisé / blessé léger). | 0/1 |
| `jour` | int64 | BAAC Caractéristiques | Jour de l’accident (1–31). | 1–31 |
| `mois` | int64 | BAAC Caractéristiques | Mois de l’accident (1–12). | 1–12 |
| `an` | int64 | BAAC Caractéristiques | Année de l’accident (ex: 2022–2024). | YYYY |
| `hrmn` | object | BAAC Caractéristiques | Heure-minute au format brut BAAC (chaîne). | HHMM ou HH:MM selon source |
| `lum` | int64 | BAAC Caractéristiques | Conditions d’éclairage (luminosité). | 1–5 (voir nomenclature) |
| `dep` | object | BAAC Caractéristiques | Département (code INSEE, incluant 2A/2B). | string |
| `com` | object | BAAC Caractéristiques | Commune (code INSEE). | string |
| `agg` | int64 | BAAC Caractéristiques | Localisation : hors/en agglomération. | 1–2 |
| `int` | int64 | BAAC Caractéristiques | Type d’intersection. | 1–9 |
| `atm` | int64 | BAAC Caractéristiques | Conditions atmosphériques. | 1–9 |
| `col` | int64 | BAAC Caractéristiques | Type de collision. | 1–7 |
| `adr` | object | BAAC Caractéristiques | Adresse postale (souvent en agglomération). | string/NA |
| `lat` | float64 | BAAC Caractéristiques | Latitude (WGS84) si disponible. | float/NA |
| `long` | float64 | BAAC Caractéristiques | Longitude (WGS84) si disponible. | float/NA |
| `gps_valid` | int64 | Feature (qualité) | 1 si coordonnées GPS jugées valides après nettoyage/correctifs, sinon 0. | 0/1 |
| `hour` | int64 | Feature (temps) | Heure extraite de hrmn/date (0–23). | 0–23 |
| `minute` | int64 | Feature (temps) | Minute extraite de hrmn/date (0–59). | 0–59 |
| `date` | object | Feature (temps) | Timestamp reconstruit à partir de jour/mois/an + hrmn. | datetime |
| `n_lieux_rows` | int64 | Feature (jointure) | Nombre de lignes LIEUX associées à Num_Acc (contrôle de jointure). | >=1 |
| `catr` | float64 | BAAC Lieux | Catégorie de route. | 1–9 |
| `voie` | object | BAAC Lieux | Numéro de route. | string/NA |
| `v1` | float64 | BAAC Lieux | Indice numérique du numéro de route (bis/ter…). | int/NA |
| `circ` | float64 | BAAC Lieux | Régime de circulation. | 1–4 |
| `nbv` | float64 | BAAC Lieux | Nombre total de voies de circulation. | int/NA |
| `vosp` | float64 | BAAC Lieux | Voie réservée (piste/bande cyclable, voie réservée…). | 0–3 |
| `prof` | float64 | BAAC Lieux | Profil en long (plat/pente/sommet/bas de côte). | 1–4 |
| `pr` | float64 | BAAC Lieux | Numéro de PR de rattachement (borne). | int/NA |
| `pr1` | float64 | BAAC Lieux | Distance au PR (m). | int/NA |
| `plan` | float64 | BAAC Lieux | Tracé en plan (rectiligne/courbe/S…). | 1–4 |
| `larrout` | float64 | BAAC Lieux | Largeur de la chaussée (m). | float/NA |
| `surf` | float64 | BAAC Lieux | État de surface (normale, mouillée, verglacée…). | 1–9 |
| `infra` | float64 | BAAC Lieux | Aménagement/infrastructure (tunnel, pont, chantier…). | 0–9 |
| `situ` | float64 | BAAC Lieux | Situation de l’accident (chaussée, BAU, trottoir…). | 0–8 |
| `vma` | float64 | BAAC Lieux | Vitesse maximale autorisée (km/h). | num/NA |
| `nb_vehicules` | int64 | Feature (agrégat véhicules) | Nombre de véhicules impliqués dans l’accident (distinct id_vehicule). | >=1 |
| `catv_mode` | float64 | Feature (agrégat véhicules) | Catégorie de véhicule (catv) la plus fréquente parmi les véhicules impliqués (mode). | Codes BAAC catv |
| `motor_mode` | float64 | Feature (agrégat véhicules) | Type de motorisation la plus fréquente (mode). | -1,0,1..6 |
| `senc_mode` | float64 | Feature (agrégat véhicules) | Sens de circulation le plus fréquent (mode). | 0–3 |
| `choc_mode` | float64 | Feature (agrégat véhicules) | Point de choc initial le plus fréquent (mode). | 0–9 |
| `manv_mode` | float64 | Feature (agrégat véhicules) | Manœuvre principale avant l’accident la plus fréquente (mode). | 0–26 |
| `catv_family_4` | object | Feature (catégorielle) | Regroupement de catv_mode en 4 familles (cardinalité réduite). | {vulnerables, 2rm_3rm, voitures_utilitaires, lourds_tc_agri_autres} |
| `obs_mode` | float64 | Feature (agrégat véhicules) | Obstacle fixe heurté (obs) le plus fréquent (mode sur tous véhicules). | 0–17 |
| `obs_family_mode` | object | Feature (catégorielle) | Regroupement de obs_mode en familles. | {sans_objet_ou_nr, vehicule_stationnement, infrastructure_urbain, nature_terrain_sortie} |
| `any_obs_fixed` | int64 | Feature (binaire) | 1 si au moins un véhicule a heurté un obstacle fixe (obs>0), sinon 0. | 0/1 |
| `any_sortie_chaussee` | int64 | Feature (binaire) | 1 si au moins un véhicule a ‘sortie de chaussée sans obstacle’ (obs==16), sinon 0. | 0/1 |
| `any_tree` | int64 | Feature (binaire) | 1 si au moins un véhicule a heurté un arbre (obs==2), sinon 0. | 0/1 |
| `obs_mode_nonzero` | float64 | Feature (agrégat véhicules) | Mode de obs en excluant 0 (‘sans objet’) pour capturer un obstacle quand il existe. | 1–17/NA |
| `obs_family_mode_nonzero` | object | Feature (catégorielle) | Famille de obs_mode_nonzero (même mapping que obs_family_mode). | voir obs_family_mode |
| `dow` | int64 | Feature (temps) | Jour de semaine (0=Lundi … 6=Dimanche, convention pandas). | 0–6 |
| `is_weekend` | int64 | Feature (temps) | 1 si samedi/dimanche, sinon 0. | 0/1 |
| `time_bucket` | object | Feature (temps) | Tranche horaire (bucket) dérivée de l’heure. | {matin, journee, soir, nuit, nuit_tard} |
| `is_rush_hour` | int64 | Feature (temps) | 1 si heure de pointe (selon règle notebook), sinon 0. | 0/1 |
| `season` | object | Feature (temps) | Saison dérivée du mois. | {hiver, printemps, ete, automne} |
| `hour_sin` | float64 | Feature (cyclique) | Encodage sinusoïdal de l’heure (cycle 24h). | float |
| `hour_cos` | float64 | Feature (cyclique) | Encodage cosinus de l’heure (cycle 24h). | float |
| `month_sin` | float64 | Feature (cyclique) | Encodage sinusoïdal du mois (cycle annuel). | float |
| `month_cos` | float64 | Feature (cyclique) | Encodage cosinus du mois (cycle annuel). | float |
| `lat_grid_2` | float64 | Feature (geo) | Latitude arrondie à 2 décimales (≈1.1 km). | float/NA |
| `long_grid_2` | float64 | Feature (geo) | Longitude arrondie à 2 décimales (≈0.7–0.8 km selon latitude). | float/NA |
| `geo_cell_2` | object | Feature (geo) | Cellule géographique ‘lat_grid_2_long_grid_2’ (catégorielle). | string/NA |
| `lat_grid_3` | float64 | Feature (geo) | Latitude arrondie à 3 décimales (≈110 m). | float/NA |
| `long_grid_3` | float64 | Feature (geo) | Longitude arrondie à 3 décimales. | float/NA |
| `geo_cell_3` | object | Feature (geo) | Cellule géographique ‘lat_grid_3_long_grid_3’ (catégorielle). | string/NA |
| `vma_bucket` | object | Feature (vitesse) | Bucket de vma (vitesse max autorisée). | {<=30,31-50,51-80,81-90,91-110,111-130,inconnue} |
| `is_high_speed` | float64 | Feature (vitesse) | 1 si vma ≥ 90 km/h, sinon 0 (NA -> 0 ou NA selon pipeline). | 0/1 |
| `is_urban_speed` | float64 | Feature (vitesse) | 1 si vma ≤ 50 km/h, sinon 0. | 0/1 |
| `is_single_vehicle` | int64 | Feature (vitesse/véhicules) | 1 si nb_vehicules==1, sinon 0. | 0/1 |
| `is_multi_vehicle` | int64 | Feature (vitesse/véhicules) | 1 si nb_vehicules>=2, sinon 0. | 0/1 |
| `veh_bucket` | object | Feature (véhicules) | Bucket du nombre de véhicules : 1 / 2 / 3 / 4+. | {1,2,3,4+} |
| `obs_fixed_x_highspeed` | int64 | Feature (interaction) | Interaction : any_obs_fixed * is_high_speed. | 0/1 |
| `tree_x_highspeed` | int64 | Feature (interaction) | Interaction : any_tree * is_high_speed. | 0/1 |
| `sortie_x_singleveh` | int64 | Feature (interaction) | Interaction : any_sortie_chaussee * is_single_vehicle. | 0/1 |
| `has_obs_nonzero` | int64 | Feature (binaire) | 1 si au moins un obstacle fixe non nul existe (obs_mode_nonzero non-NA), sinon 0. | 0/1 |
| `lum_num` | int64 | Feature (nettoyage) | Version numérique nettoyée de lum (sans valeurs NR résiduelles). | 1–5 |
| `atm_num` | int64 | Feature (nettoyage) | Version numérique nettoyée de atm (sans valeurs NR résiduelles). | 1–9 |
| `is_night_proxy` | int64 | Feature (proxy) | 1 si conditions d’éclairage != plein jour (lum in {2,3,4,5}), sinon 0. | 0/1 |
| `is_bad_weather_proxy` | int64 | Feature (proxy) | 1 si conditions atmosphériques != normale (atm in {2..9}), sinon 0. | 0/1 |
| `night_x_bad_weather` | int64 | Feature (interaction) | Interaction : is_night_proxy * is_bad_weather_proxy. | 0/1 |

## 2) Nomenclatures BAAC utiles (extraits)

### 2.1 Caractéristiques
- `lum` (lumière) :
  1 plein jour ; 2 crépuscule/aube ; 3 nuit sans éclairage public ; 4 nuit éclairage non allumé ; 5 nuit éclairage allumé.
- `agg` (localisation) : 1 hors agglomération ; 2 en agglomération.
- `int` (intersection) : 1 hors intersection ; 2 en X ; 3 en T ; 4 en Y ; 5 >4 branches ; 6 giratoire ; 7 place ; 8 passage à niveau ; 9 autre.
- `atm` (conditions atmosphériques) : 1 normale ; 2 pluie légère ; 3 pluie forte ; 4 neige/grêle ; 5 brouillard/fumée ; 6 vent fort/tempête ; 7 temps éblouissant ; 8 couvert ; 9 autre.
- `col` (type de collision) : 1 frontale ; 2 arrière ; 3 côté ; 4 chaîne (≥3) ; 5 multiples (≥3) ; 6 autre ; 7 sans collision.

### 2.2 Lieux
- `catr` (catégorie route) : 1 autoroute ; 2 nationale ; 3 départementale ; 4 voie communale ; 5 hors réseau public ; 6 parking public ; 7 métropole urbaine ; 9 autre.
- `circ` : 1 sens unique ; 2 bidirectionnelle ; 3 chaussées séparées ; 4 voies à affectation variable.
- `vosp` : 0 sans objet ; 1 piste cyclable ; 2 bande cyclable ; 3 voie réservée.
- `prof` : 1 plat ; 2 pente ; 3 sommet de côte ; 4 bas de côte.
- `plan` : 1 rectiligne ; 2 courbe gauche ; 3 courbe droite ; 4 en S.
- `surf` : 1 normale ; 2 mouillée ; 3 flaques ; 4 inondée ; 5 enneigée ; 6 boue ; 7 verglacée ; 8 corps gras/huile ; 9 autre.
- `infra` : 0 aucun ; 1 tunnel ; 2 pont ; 3 bretelle ; 4 voie ferrée ; 5 carrefour aménagé ; 6 zone piétonne ; 7 péage ; 8 chantier ; 9 autres.
- `situ` : 0 aucun ; 1 chaussée ; 2 BAU ; 3 accotement ; 4 trottoir ; 5 piste cyclable ; 6 autre voie spéciale ; 8 autres.
- `vma` : vitesse max autorisée au lieu/moment de l’accident (km/h).

### 2.3 Véhicules (si tu veux interpréter `*_mode`)
- `senc` (sens) : 0 inconnu ; 1 repère croissant ; 2 repère décroissant ; 3 absence de repère.
- `catv` : liste longue (exemples fréquents) :
  01 bicyclette ; 02 cyclomoteur <50 ; 03 voiturette ; 07 VL ; 10 VU ; 13/14/15 PL ; 16/17 tracteur routier ; 21 tracteur agricole ; 30+ deux-roues >50 ; 37 autobus ; 38 autocar ; 50 EDP moteur ; 60 EDP sans moteur ; 80 VAE ; 99 autre.
- `motor` (motorisation) : 1 hydrocarbures ; 2 hybride ; 3 électrique ; 4 hydrogène ; 5 humaine ; 6 autre.
- `obs` (obstacle fixe) : 0 sans objet ; 1 véhicule stationné ; 2 arbre ; 3 glissière métal ; 4 glissière béton ; … ; 16 sortie de chaussée sans obstacle ; 17 buse/tête d’aqueduc.
- `choc` (point de choc) : 0 aucun ; 1 avant ; 2 avant droit ; 3 avant gauche ; 4 arrière ; 5 arrière droit ; 6 arrière gauche ; 7 côté droit ; 8 côté gauche ; 9 chocs multiples.
- `manv` (manœuvre) : 1 sans changement direction ; 2 même sens même file ; 3 entre 2 files ; … ; 19 traversant chaussée ; 20 stationnement ; 21 évitement ; 22 ouverture porte ; 23 arrêté ; 24 en stationnement ; 25 sur trottoir ; 26 autre.

## 3) Construction des features (règles observées dans ton CSV)

### 3.1 Temps
- `dow` : jour de semaine (0=Lundi … 6=Dimanche).
- `is_weekend` : 1 si `dow` ∈ {5,6}.
- `time_bucket` (selon tes données) :
  - `nuit` : 00–05
  - `matin` : 06–09
  - `journee` : 10–16
  - `soir` : 17–20
  - `nuit_tard` : 21–23
- `is_rush_hour` : 1 si heure ∈ {7,8,9,16,17,18,19}.
- `season` :
  - hiver = {12,1,2}
  - printemps = {3,4,5}
  - été = {6,7,8}
  - automne = {9,10,11}
- `hour_sin/hour_cos`, `month_sin/month_cos` : encodage cyclique (sin/cos).

### 3.2 Géographie
- `lat_grid_2/long_grid_2` : arrondi à 2 décimales ; `geo_cell_2` = concat “lat_long”.
- `lat_grid_3/long_grid_3` : arrondi à 3 décimales ; `geo_cell_3` = concat “lat_long”.
- `gps_valid` : drapeau de validité GPS après nettoyage.

### 3.3 Vitesse / véhicules / obstacles
- `vma_bucket` : bucketisation de `vma` (<=30, 31–50, 51–80, 81–90, 91–110, 111–130, inconnue).
- `is_high_speed` : 1 si `vma` ≥ 90.
- `is_urban_speed` : 1 si `vma` ≤ 50.
- `veh_bucket` : {1,2,3,4+} dérivé de `nb_vehicules`.
- `catv_family_4` (4 familles) :
  - `vulnerables` : vélos + EDP + autres très légers (ex: 01, 60, 80…)
  - `2rm_3rm` : 2 roues / 3 roues motorisés (ex: 02, 30–34, 41–43…)
  - `voitures_utilitaires` : VL/VU (ex: 07, 10…)
  - `lourds_tc_agri_autres` : PL, bus/car, agricole, train/tram, engins, autres (ex: 13–17, 20–21, 37–40, 99…)
- Obstacles :
  - `obs_mode` = mode de `obs` sur les véhicules
  - `obs_mode_nonzero` = mode de `obs` en excluant 0 (permet de “voir” un obstacle si présent)
  - `has_obs_nonzero` = 1 si `obs_mode_nonzero` non NA
  - `any_tree` = 1 si au moins un `obs==2`
  - `any_sortie_chaussee` = 1 si au moins un `obs==16`
  - Interactions : `tree_x_highspeed`, `obs_fixed_x_highspeed`, `sortie_x_singleveh`

### 3.4 Proxies météo / nuit (issus de codes BAAC)
- `is_night_proxy` = 1 si `lum` ∈ {2,3,4,5}
- `is_bad_weather_proxy` = 1 si `atm` ∈ {2,3,4,5,6,7,8,9}
- `night_x_bad_weather` = interaction des deux

## 4) Note importante — features “conducteur” (sexe/âge/trajet)
Ce CSV final (celui fourni ici) **ne contient pas** les colonnes conducteur (`any_female_driver`, `driver_age_bucket`, `driver_trajet_family`, etc.).

Si tu veux que je produise un *data dictionary* “V2 conducteur” complet, il faut que le CSV final exporté par FeatureEngineering inclue bien ces colonnes (ou que tu me donnes `accidents_model_ready_with_driver*.csv`).
Les codes BAAC nécessaires côté usagers :
- `catu` (1 conducteur / 2 passager / 3 piéton)
- `grav` (1 indemne / 2 tué / 3 blessé hospitalisé / 4 blessé léger)
- `sexe` (1 masculin / 2 féminin)
- `an_nais` (année de naissance)
- `trajet` (1 domicile-travail / 2 domicile-école / 3 courses-achats / 4 pro / 5 loisirs / 9 autre)
