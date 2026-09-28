# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# Updated for Week 15 (Sep 28 - Oct 4, 2026) - ACTIVE RECOVERY CUTBACK (38-40 KM)

week_start = "2026-09-28"
week_end   = "2026-10-04"
generated  = "2026-09-28"

plan = {
    "meta": {
        "week":        "September 28 – October 4, 2026",
        "phase":       "Active Recovery Cutback | Week 15 (Neuromuscular & Tendon Remodeling)",
        "load_target": "38–40 km | Long Run: 16.0 km",
        "objective":   "Allow quad fasciculations and knee crepitus to fully resolve after Saturday's 21.39 km HM PB match in high heat. 30k long run deferred to Week 16 (Oct 11). Keep all running strictly in Zone 2 with zero high-intensity speed repeats.",
        "acwr_context":"Mechanical ACWR safely controlled (~1.12). VO2 Max hit 59 ml/kg/min (all-time high). Sunday 3k treadmill flush completed on Sep 27.",
        "zone_update": "Zone 1: <162 bpm. Zone 2: 162–174 bpm. Max HR: 206 bpm.",
        "injury_note": "Painless quad fasciculations & knee crepitus management: 400mg Magnesium Glycinate daily + hydration electrolytes + outer quad foam rolling.",
        "facility_note":"Anytime Fitness Taft, Condo Gym, Marikina Indoor Bike on Thursday.",
    },
    "days": {
        "2026-09-28": {
            "label":   "Monday | Upper Push Hypertrophy & Core [AF Taft]",
            "session": "Upper Body Push & Core (0.0 km Running Impact)",
            "detail":  "40-45m Upper Push: Seated Chest Press (4x8-12), Incline DB Press (3x10-12), Cable Tricep Rope Pushdowns (4x12-15), DB Lateral Raises (3x12-15), Core Planks/Leg Raises (3x). STRICT VETO ON LEGS.",
            "run_km":  0.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-29": {
            "label":   "Tuesday | Zone 2 Aerobic Cruise [6K] (Pure Run Focus)",
            "session": "6.0 km Zone 2 Aerobic Cruise (162–172 bpm)",
            "detail":  "Controlled aerobic base cruise (0% treadmill or flat road). Pure running focus with upper push strength already completed Monday.",
            "run_km":  6.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-30": {
            "label":   "Wednesday | Zone 2 Aerobic Cruise + Strides [7.5K]",
            "session": "7.5 km: 6.0 km Zone 2 Cruise + 4x100m Relaxed Strides (~3:45-3:55/km)",
            "detail":  "Smooth Zone 2 volume followed by 4 light acceleration strides to maintain neural turnover without metabolic strain.",
            "run_km":  7.5,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-01": {
            "label":   "Thursday | Marikina Indoor Bike Flush [35m] + Upper Pull Strength",
            "session": "35m Indoor Bike Flush (Zone 1, <125 bpm, 85-90 rpm) + Upper Pull Strength",
            "detail":  "Marikina logistics: 35m light spinning (0.0 ground reaction force) + Lat pulldowns, rows, rear delts, and core. (NO SWIMMING).",
            "run_km":  0.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-02": {
            "label":   "Friday | Pre-Long Run Priming Shakeout [4K]",
            "session": "4.0 km Flat Easy Shakeout (<148 bpm, Zone 1) + High-Carb Fueling",
            "detail":  "Easy 4.0 km flat shakeout in Puma Velocity Nitro 3s. Carb loading day for Saturday's 16k cutback long run.",
            "run_km":  4.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-03": {
            "label":   "Saturday | Cutback Aerobic Long Run [16K]",
            "session": "16.0 km Steady Zone 2 Cruise (162–172 bpm)",
            "detail":  "Regulated 16.0 km cutback long run in Marikina. Fuel with 2 energy gels at Km 6 and 12.",
            "run_km":  16.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-04": {
            "label":   "Sunday | Full Rest & Neuromuscular Reset",
            "session": "FULL REST DAY (0.0 km)",
            "detail":  "Complete rest day. Foam roll outer quads, mobility, and recovery.",
            "run_km":  0.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
    }
}

if __name__ == "__main__":
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")
    print(f"=== WEEKLY PLAN: {plan['meta']['week']} ===")
    print(f"Phase:    {plan['meta']['phase']}")
    print(f"Load:     {plan['meta']['load_target']}")
    if today in plan["days"]:
        d = plan["days"][today]
        print(f"\nTODAY ({today}):")
        print(f"  {d['label']} — {d['session']}")
        print(f"  {d['detail']}")
    else:
        print("\nFull week:")
        for dt, d in plan["days"].items():
            print(f"  {dt}: {d['label']} — {d['session']}")
