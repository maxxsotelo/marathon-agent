# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# Updated for Week 15 (Sep 28 - Oct 4, 2026) - ACTIVE RECOVERY CUTBACK (38-40 KM)

week_start = "2026-09-28"
week_end   = "2026-10-04"
generated  = "2026-10-01"

plan = {
    "meta": {
        "week":        "September 28 – October 4, 2026",
        "phase":       "Active Recovery Cutback | Week 15 (Neuromuscular & Tendon Remodeling)",
        "load_target": "38–40 km | Long Run: 16.0 km",
        "objective":   "Allow quad fasciculations and knee crepitus to fully resolve after Saturday's 21.39 km HM PB match in high heat. 30k long run deferred to Week 16 (Oct 11). Keep all running strictly in Zone 2 with zero high-intensity speed repeats.",
        "acwr_context":"Mechanical ACWR safely controlled (~1.12). VO2 Max hit 59 ml/kg/min (all-time high). Thursday coached pull + bike flush completed on Oct 1.",
        "zone_update": "Zone 1: <162 bpm. Zone 2: 162–174 bpm. Max HR: 206 bpm.",
        "injury_note": "Painless quad fasciculations & knee crepitus management: 400mg Magnesium Glycinate daily + hydration electrolytes + outer quad foam rolling.",
        "facility_note":"Anytime Fitness Taft, Condo Gym, Marikina Indoor Bike on Thursday.",
    },
    "days": {
        "2026-09-28": {
            "label":   "Monday | Boxing (21m) + Upper Push Hypertrophy & Core [AF Taft]",
            "session": "COMPLETED: Boxing (21m, TE 2.4) + Upper Push & Core (38m, TE 0.6)",
            "detail":  "427 active kcal burned. Seated Chest Press, Incline DB Press, Cable Triceps, Lateral Raises, Core.",
            "run_km":  0.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-29": {
            "label":   "Tuesday | Zone 2 Aerobic Cruise [6.14K COMPLETED]",
            "session": "COMPLETED: 6.14 km @ 5:09/km (Avg HR 158 bpm, TE 3.4)",
            "detail":  "Maiden flight of Adidas Supernova Hyperboost Edge (106.14k total). Perfect Z2 compliance in 32°C wrist heat index.",
            "run_km":  6.14,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-30": {
            "label":   "Wednesday | Zone 2 Cruise + Strides [6.78K] + Core/Prehab [COMPLETED]",
            "session": "COMPLETED: 6.78 km @ 5:39/km (Strides at 9.3-10.0 mph, TE 3.1) + Core/Prehab (29.7m)",
            "detail":  "Flawless Zone 2 control (Avg HR 150 bpm) + 4x100m strides + 30m rotational core, leg raises, rotator cuff prehab, and forearms.",
            "run_km":  6.78,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-01": {
            "label":   "Thursday | Coached Upper Pull (66m) + Bike Flush (27m) + Core [COMPLETED]",
            "session": "COMPLETED: Coached Pull (66.4m, 301 kcal) + Indoor Bike Flush (26.8m, 146 kcal) + Leg Raises (6m)",
            "detail":  "Marikina Base: Coached Pull Day with Coach Kent (Lats, Upper Back, Rear Delts, Biceps) + 26.8m Indoor Bike Flush (Avg HR 104 bpm) + Hanging Leg Raises. 0.0 RUN IMPACT.",
            "run_km":  0.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-10-02": {
            "label":   "Friday | Pre-Long Run Priming Shakeout [4K]",
            "session": "4.0 km Flat Easy Shakeout (<148 bpm, Zone 1) + High-Carb Fueling",
            "detail":  "Easy 4.0 km flat shakeout in Ultraboost 5X. Carb loading day for Saturday's 16k cutback long run.",
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
