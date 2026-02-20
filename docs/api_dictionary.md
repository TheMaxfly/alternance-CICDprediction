# API Data Dictionary — accidents_model_ready.csv (Model-Ready)

## Objectif
Ce schéma décrit le format **attendu par le modèle** pour prédire la cible `grave` à partir d’une ligne "accident-level" feature-engineered.

- Granularité : 1 enregistrement = 1 accident (`Num_Acc` unique).
- Période d’entraînement : 2022–2024.
- Cible d’entraînement (non fournie à l’inférence) : `grave`.
  - `grave = 1` : accident grave (au moins 1 tué ou blessé hospitalisé)
  - `grave = 0` : accident non grave (au pire blessé léger)
  > Remarque : en accident-level BAAC, il n’y a généralement pas de classe “tous indemnes”.

---

## 1) JSON Schema (Draft 2020-12) — Request / Response

### 1.1 Request (Batch)
- Endpoint (exemple) : `POST /predict`
- Le serveur accepte un batch (`records`) et retourne un batch de prédictions.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/accident-model-ready-request.json",
  "title": "AccidentModelReadyBatchRequest",
  "type": "object",
  "required": ["records"],
  "properties": {
    "model_version": { "type": "string" },
    "records": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/AccidentModelReadyRecord" }
    }
  },
  "$defs": {
    "AccidentModelReadyRecord": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "Num_Acc": { "type": ["integer","string"], "description": "Identifiant accident (optionnel côté API, utile pour tracer la prédiction)." },

        "jour": { "type": ["integer","null"], "minimum": 1, "maximum": 31 },
        "mois": { "type": ["integer","null"], "minimum": 1, "maximum": 12 },
        "an":   { "type": ["integer","null"], "minimum": 2005, "maximum": 2100 },

        "hrmn": { "type": ["string","null"], "description": "Heure brute BAAC (ex: '0830')." },

        "lum": { "type": ["integer","null"], "enum": [1,2,3,4,5], "description": "Luminosité BAAC." },
        "dep": { "type": ["string","null"], "description": "Département (code INSEE, ex: '59', '2A')." },
        "com": { "type": ["string","null"], "description": "Commune (code INSEE)." },
        "agg": { "type": ["integer","null"], "description": "Agglomération BAAC (souvent 1/2)." },
        "int": { "type": ["integer","null"], "description": "Intersection BAAC (codes)." },
        "atm": { "type": ["integer","null"], "enum": [1,2,3,4,5,6,7,8,9], "description": "Conditions atmosphériques BAAC." },
        "col": { "type": ["integer","null"], "description": "Type de collision BAAC (codes)." },

        "adr":  { "type": ["string","null"], "description": "Adresse (souvent partielle)." },
        "lat":  { "type": ["number","null"], "minimum": -90, "maximum": 90 },
        "long": { "type": ["number","null"], "minimum": -180, "maximum": 180 },
        "gps_valid": { "type": ["integer","null"], "enum": [0,1], "description": "1 si GPS validé après nettoyage." },

        "hour":   { "type": ["integer","null"], "minimum": 0, "maximum": 23 },
        "time_bucket": {
          "type": ["string","null"],
          "enum": ["night_00_05", "morning_06_11", "afternoon_12_17", "evening_18_23"],
          "description": "Tranche horaire (00–05 night_00_05, 06–11 morning_06_11, 12–17 afternoon_12_17, 18–23 evening_18_23)."
        },
        "date":   { "type": ["string","null"], "format": "date-time", "description": "Timestamp reconstruit." },

        "n_lieux_rows": { "type": ["integer","null"], "minimum": 1, "description": "Nb de lignes LIEUX agrégées." },
        "catr": { "type": ["number","null"], "description": "Catégorie route BAAC (codes)." },
        "voie": { "type": ["string","null"], "description": "Numéro de voie (forte cardinalité)." },
        "v1":   { "type": ["number","null"], "description": "Indice route (bis/ter...)."},
        "circ": { "type": ["number","null"], "description": "Régime circulation BAAC (codes)." },
        "nbv":  { "type": ["number","null"], "description": "Nombre de voies." },
        "vosp": { "type": ["number","null"], "description": "Voie réservée BAAC (codes)." },
        "prof": { "type": ["number","null"], "description": "Profil BAAC (codes)." },
        "pr":   { "type": ["number","null"], "description": "PR." },
        "pr1":  { "type": ["number","null"], "description": "Distance au PR." },
        "plan": { "type": ["number","null"], "description": "Tracé en plan BAAC (codes)." },
        "larrout": { "type": ["number","null"], "description": "Largeur chaussée (souvent manquant)." },
        "surf": { "type": ["number","null"], "description": "État surface BAAC (codes)." },
        "infra": { "type": ["number","null"], "description": "Infrastructure BAAC (codes)." },
        "situ": { "type": ["number","null"], "description": "Situation BAAC (codes)." },
        "vma":  { "type": ["number","null"], "minimum": 10, "maximum": 200, "description": "Vitesse max autorisée (km/h), nettoyée." },

        "nb_vehicules": { "type": ["integer","null"], "minimum": 1 },
        "catv_mode": { "type": ["number","null"], "description": "Catégorie véhicule (mode) BAAC." },
        "motor_mode": { "type": ["number","null"], "description": "Motorisation (mode) BAAC." },
        "senc_mode":  { "type": ["number","null"], "description": "Sens (mode) BAAC." },
        "choc_mode":  { "type": ["number","null"], "description": "Point de choc (mode) BAAC." },
        "manv_mode":  { "type": ["number","null"], "description": "Manœuvre (mode) BAAC." },

        "catv_family_4": {
          "type": ["string","null"],
          "enum": ["vulnerables","2rm_3rm","voitures_utilitaires","lourds_tc_agri_autres"]
        },

        "obs_mode": { "type": ["number","null"], "description": "Obstacle fixe (mode) BAAC." },
        "obs_family_mode": {
          "type": ["string","null"],
          "enum": ["sans_objet_ou_nr","vehicule_stationnement","infrastructure_urbain","nature_terrain_sortie"]
        },
        "any_obs_fixed": { "type": ["integer","null"], "enum": [0,1] },
        "any_sortie_chaussee": { "type": ["integer","null"], "enum": [0,1] },
        "any_tree": { "type": ["integer","null"], "enum": [0,1] },
        "obs_mode_nonzero": { "type": ["number","null"], "description": "Obstacle mode en excluant 0 (sans objet)." },
        "obs_family_mode_nonzero": {
          "type": ["string","null"],
          "enum": ["vehicule_stationnement","infrastructure_urbain","nature_terrain_sortie"]
        },

        "nb_drivers": { "type": ["integer","null"], "minimum": 0 },
        "driver_sex_mode": { "type": ["integer","null"], "enum": [1,2], "description": "1=Homme, 2=Femme (mode conducteur)." },
        "any_female_driver": { "type": ["integer","null"], "enum": [0,1] },
        "any_male_driver": { "type": ["integer","null"], "enum": [0,1] },
        "female_driver_share": { "type": ["number","null"], "minimum": 0, "maximum": 1 },

        "driver_age_mean": { "type": ["number","null"], "minimum": 14, "maximum": 110 },
        "driver_age_median": { "type": ["number","null"], "minimum": 14, "maximum": 110 },
        "driver_age_min": { "type": ["number","null"], "minimum": 14, "maximum": 110 },
        "driver_age_max": { "type": ["number","null"], "minimum": 14, "maximum": 110 },

        "driver_trajet_mode": { "type": ["integer","null"], "description": "Trajet conducteur (code BAAC) mode." },
        "driver_info_missing": { "type": ["integer","null"], "enum": [0,1] },

        "driver_age_bucket": {
          "type": ["string","null"],
          "enum": ["<18","18-24","25-34","35-44","45-54","55-64","65-74","75+","unknown"]
        },
        "driver_trajet_family": {
          "type": ["string","null"],
          "enum": ["trajet_1","trajet_2","trajet_3","trajet_4","trajet_5","trajet_9","unknown"]
        },

        "dow": { "type": ["integer","null"], "minimum": 0, "maximum": 6 },
        "is_weekend": { "type": ["integer","null"], "enum": [0,1] },
        "time_bucket": { "type": ["string","null"], "enum": ["night_00_05","morning_06_11","afternoon_12_17","evening_18_23"] },
        "is_rush_hour": { "type": ["integer","null"], "enum": [0,1] },
        "season": { "type": ["string","null"], "enum": ["hiver","printemps","ete","automne"] },

        "hour_sin": { "type": ["number","null"] },
        "hour_cos": { "type": ["number","null"] },
        "month_sin": { "type": ["number","null"] },
        "month_cos": { "type": ["number","null"] },

        "lat_grid_2": { "type": ["number","null"] },
        "long_grid_2": { "type": ["number","null"] },
        "geo_cell_2": { "type": ["string","null"], "description": "Cellule géo ~1km (catégorielle)." },
        "lat_grid_3": { "type": ["number","null"] },
        "long_grid_3": { "type": ["number","null"] },
        "geo_cell_3": { "type": ["string","null"], "description": "Cellule géo ~100m (catégorielle)." },

        "vma_bucket": {
          "type": ["string","null"],
          "enum": ["<=30","31-50","51-80","81-90","91-110","111-130",">130","inconnue"]
        },
        "is_high_speed": { "type": ["integer","null"], "enum": [0,1] },
        "is_urban_speed": { "type": ["integer","null"], "enum": [0,1] },
        "is_single_vehicle": { "type": ["integer","null"], "enum": [0,1] },
        "is_multi_vehicle": { "type": ["integer","null"], "enum": [0,1] },
        "veh_bucket": { "type": ["string","null"], "enum": ["1","2","3","4+"] },

        "obs_fixed_x_highspeed": { "type": ["integer","null"], "enum": [0,1] },
        "tree_x_highspeed": { "type": ["integer","null"], "enum": [0,1] },
        "sortie_x_singleveh": { "type": ["integer","null"], "enum": [0,1] },
        "has_obs_nonzero": { "type": ["integer","null"], "enum": [0,1] },

        "atm_num": { "type": ["integer","null"], "enum": [1,2,3,4,5,6,7,8,9] },
        "lum_num": { "type": ["integer","null"], "enum": [1,2,3,4,5] },

        "atm_label": {
          "type": ["string","null"],
          "enum": ["normale","pluie_legere","pluie_forte","neige_grele","brouillard_fumee","vent_fort_tempete","temps_eblouissant","temps_couvert","autre"]
        },
        "lum_label": {
          "type": ["string","null"],
          "enum": ["plein_jour","crepuscule_aube","nuit_sans_eclairage","nuit_eclairage_non_allume","nuit_eclairage_allume"]
        },
        "atm_family": {
          "type": ["string","null"],
          "enum": ["normal","pluie","neige_grele","brouillard_fumee","vent_tempete","eblouissant","couvert","autre"]
        },
        "lum_family": {
          "type": ["string","null"],
          "enum": ["jour","crepuscule","nuit"]
        },

        "is_night": { "type": ["integer","null"], "enum": [0,1] },
        "is_twilight": { "type": ["integer","null"], "enum": [0,1] },
        "is_daylight": { "type": ["integer","null"], "enum": [0,1] },

        "is_rain": { "type": ["integer","null"], "enum": [0,1] },
        "is_fog": { "type": ["integer","null"], "enum": [0,1] },
        "is_snow_hail": { "type": ["integer","null"], "enum": [0,1] },
        "is_storm_wind": { "type": ["integer","null"], "enum": [0,1] },
        "is_glare": { "type": ["integer","null"], "enum": [0,1] },
        "is_overcast": { "type": ["integer","null"], "enum": [0,1] },

        "night_x_rain": { "type": ["integer","null"], "enum": [0,1] },
        "night_x_fog": { "type": ["integer","null"], "enum": [0,1] }
      }
    }
  }
}



"""Response (Batch)

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.org/schemas/accident-model-ready-response.json",
  "title": "AccidentModelReadyBatchResponse",
  "type": "object",
  "required": ["predictions"],
  "properties": {
    "model_version": { "type": "string" },
    "predictions": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["grave_pred", "grave_proba"],
        "properties": {
          "Num_Acc": { "type": ["integer","string","null"] },
          "grave_pred": { "type": "integer", "enum": [0,1] },
          "grave_proba": { "type": "number", "minimum": 0, "maximum": 1 }
        }
      }
    }
  }
}
