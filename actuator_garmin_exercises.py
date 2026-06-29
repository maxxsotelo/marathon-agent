# ─────────────────────────────────────────────────────────────────────────────
# GARMIN CONNECT — EXERCISE CATEGORY & NAME REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
# Validated 2026-06-03 via live API round-trip testing.
#
# WEIGHT UNIT:
#   {"unitId": 8, "unitKey": "kilogram", "factor": 1000.0}
#
# RULES:
#   1. ALWAYS set `category` and `exerciseName` on every ExecutableStep.
#   2. ALWAYS set `weightValue` + `weightUnit` for weighted exercises.
#   3. If the exact exerciseName is not in the MATCH list below,
#      use the category with exerciseName=None. Garmin will display the
#      correct category icon on the watch but won't pre-select the exercise.
#   4. NEVER use category "DIP" or "CHEST" — they are rejected by the API.
#      Use BENCH_PRESS as the fallback category for dips.
# ─────────────────────────────────────────────────────────────────────────────

KG_UNIT = {"unitId": 8, "unitKey": "kilogram", "factor": 1000.0}

# ── FULLY VALIDATED (category + exerciseName both accepted) ──────────────────
# These will show the correct exercise name AND category on the watch.
EXERCISES = {
    # Upper Body
    "weighted_pull_up":     {"category": "PULL_UP",         "exerciseName": "WEIGHTED_PULL_UP"},
    "pull_up":              {"category": "PULL_UP",         "exerciseName": "PULL_UP"},
    "overhead_press_bb":    {"category": "SHOULDER_PRESS",  "exerciseName": "OVERHEAD_BARBELL_PRESS"},
    "barbell_row":          {"category": "ROW",             "exerciseName": "BARBELL_ROW"},
    "reverse_grip_row":     {"category": "ROW",             "exerciseName": "REVERSE_GRIP_BARBELL_ROW"},

    # Lower Body — VALIDATED 2026-06-13 (corrected from user edits)
    "back_squat":           {"category": "SQUAT",           "exerciseName": "BARBELL_BACK_SQUAT"},
    "front_squat":          {"category": "SQUAT",           "exerciseName": "FRONT_SQUAT"},
    "goblet_squat":         {"category": "SQUAT",           "exerciseName": "GOBLET_SQUAT"},
    "hack_squat":           {"category": "SQUAT",           "exerciseName": "HACK_SQUAT"},
    "leg_press":            {"category": "SQUAT",           "exerciseName": "LEG_PRESS"},
    "leg_extension":        {"category": "CRUNCH",          "exerciseName": "LEG_EXTENSIONS"},   # NOT SQUAT — Garmin catalogs this under CRUNCH
    "leg_curl":             {"category": "LEG_CURL",        "exerciseName": "LEG_CURL"},          # LEG_CURL is its own category
    "seated_leg_curl":      {"category": "DEADLIFT",        "exerciseName": None},               # SEATED_LEG_CURL not a valid exerciseName
    "romanian_deadlift":    {"category": "DEADLIFT",        "exerciseName": "ROMANIAN_DEADLIFT"},
    "nordic_hamstring":     {"category": "DEADLIFT",        "exerciseName": "NORDIC_HAMSTRING_CURL"},
    "hip_abductor":         {"category": "HIP_STABILITY",   "exerciseName": None},               # HIP_ABDUCTOR not a valid exerciseName under HIP_STABILITY
    "barbell_deadlift":     {"category": "DEADLIFT",        "exerciseName": "BARBELL_DEADLIFT"},
    "seated_calf_raise":    {"category": "CALF_RAISE",      "exerciseName": "SEATED_CALF_RAISE"},

    # Plyometrics
    "box_jump":             {"category": "PLYO",            "exerciseName": "BOX_JUMP"},
    "jump_squat":           {"category": "PLYO",            "exerciseName": "JUMP_SQUAT"},

    # Core
    "plank":                {"category": "PLANK",           "exerciseName": "PLANK"},
    "side_plank":           {"category": "PLANK",           "exerciseName": "SIDE_PLANK"},
}

# ── CATEGORY-ONLY (category accepted, exerciseName falls back to generic) ────
# These will show the correct category icon but "Choose an Exercise" on Connect.
# Still FAR better than no category at all (the old behavior).
EXERCISES_CATEGORY_ONLY = {
    # Upper Body
    "weighted_dip":         {"category": "BENCH_PRESS",     "exerciseName": None},  # DIP category rejected
    "dumbbell_curl":        {"category": "CURL",            "exerciseName": None},
    "skull_crusher":        {"category": "TRICEPS_EXTENSION","exerciseName": None},

    # Lower Body
    "single_leg_rdl":       {"category": "DEADLIFT",        "exerciseName": None},

    # Plyometrics
    "broad_jump":           {"category": "PLYO",            "exerciseName": None},
    "box_jump_over":        {"category": "PLYO",            "exerciseName": None},
    "single_leg_jump":      {"category": "PLYO",            "exerciseName": None},

    # Core — VALIDATED specific exercise names (corrected from user edits 2026-06-13)
    "dead_bug":             {"category": "HIP_STABILITY",   "exerciseName": "DEAD_BUG"},         # NOT CORE — Garmin catalogs under HIP_STABILITY
    "hanging_leg_raise":    {"category": "CRUNCH",          "exerciseName": "HANGING_LEG_RAISE"},
    "leg_raise":            {"category": "CRUNCH",          "exerciseName": "LEG_RAISE"},
    "ab_rollout":           {"category": "CORE",            "exerciseName": "BARBELL_ROLLOUT"},   # NOT AB_WHEEL_ROLLOUT
    "cable_core_press":     {"category": "CORE",            "exerciseName": "CABLE_CORE_PRESS"},  # Pallof Press

    # Band / Stability
    "lateral_band_walk":    {"category": "HIP_STABILITY",   "exerciseName": None},
    "band_lateral_raise":   {"category": "LATERAL_RAISE",   "exerciseName": None},
}

# Merge both dicts for easy lookup
ALL_EXERCISES = {**EXERCISES, **EXERCISES_CATEGORY_ONLY}

# ── INVALID CATEGORIES (DO NOT USE) ─────────────────────────────────────────
# DIP   → API returns 400 "Invalid category"
# CHEST → API returns 400 "Invalid category"
