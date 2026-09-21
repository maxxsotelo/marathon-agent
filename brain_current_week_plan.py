# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# Updated for Week 14 (Sep 21 - Sep 27, 2026) - BUILD II / PEAK STEP-UP

week_start = "2026-09-21"
week_end   = "2026-09-27"
generated  = "2026-09-21"

plan = {
    "meta": {
        "week":        "September 21 – September 27, 2026",
        "phase":       "Build II / Peak | Week 14 (Endurance Step-Up & Threshold Sharpness)",
        "load_target": "50–52 km | Long Run: 24.0 km",
        "objective":   "Building on Week 13's 45.88 km volume and Saturday's 20.07 km rolling hill milestone (+179m). Step up volume cleanly into Build II with a controlled 24.0 km long run on Sunday, sharpen threshold speed on Wednesday (5x1,000m), and maintain mechanical ACWR safely at ~1.08–1.12.",
        "acwr_context":"Mechanical ACWR starts at 0.907. Vitals pristine (HRV 105 ms, RHR 40 bpm, 91m deep sleep).",
        "zone_update": "Zone 2: 162–174 bpm. Threshold: 181–191 bpm. LTHR: 191 bpm. Max HR: 206 bpm.",
        "injury_note": "Zero structural symptoms. Use Adidas EVO SL for road runs/tempo, Puma Velocity Nitro 3 for treadmill and easy miles.",
        "facility_note":"Anytime Fitness Taft (primary gym/treadmill), Condo Pool (Tue-Sun), and BSP Employee Gym.",
    },
    "days": {
        "2026-09-21": {
            "label":   "Monday | Active Recovery Flush / Shakeout",
            "session": "4.0 – 5.0 km Easy Shakeout (<150 bpm) OR Full Rest (Walking commutes logged)",
            "detail":  "Post-weekend recovery following Saturday's 20.07 km run and Sunday's 3k shakeout. Run 4k easy at AF Taft or take full rest. Low intensity only.",
            "run_km":  4.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-22": {
            "label":   "Tuesday | Aerobic Base Cruise + Upper Push",
            "session": "7.0 km Zone 2 Aerobic Cruise (162–172 bpm) + Upper Body Push & Core at AF Taft",
            "detail":  "Controlled steady aerobic running. Keep cadence snappy (175+ spm). Pair with chest/shoulder/tricep strength at AF Taft.",
            "run_km":  7.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-23": {
            "label":   "Wednesday | Quality Threshold Speed Anchor",
            "session": "8.5 km Total (2k WU + 5 x 1,000m Threshold @ 4:15–4:25/km with 90s jog recovery + 1.5k CD)",
            "detail":  "The weekly speed anchor. Sharpen lactate clearance and marathon pace reserve. Treadmill (1.0% incline) at AF Taft or outdoor route.",
            "run_km":  8.5,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-24": {
            "label":   "Thursday | Condo Pool Hydrotherapy Flush + Upper Pull",
            "session": "35m Condo Pool Swim / Decompression + Upper Pull Strength (0.0 km Running Impact)",
            "detail":  "0.0 ground reaction force. Hydrostatic pool flush reduces calf and Achilles tightness. Upper pull (lat pulldowns, rows) at AF Taft or BSP gym.",
            "run_km":  0.0,
            "gym":     True,
            "pool":    True,
            "plyo":    False,
        },
        "2026-09-25": {
            "label":   "Friday | Aerobic Foundation + Neuromuscular Strides",
            "session": "7.5 km Zone 2 Aerobic Cruise (162–172 bpm) + 4 x 100m Relaxed Strides",
            "detail":  "Smooth aerobic volume with light strides at the end to open up the hips and prime neuromuscular turnover before the weekend.",
            "run_km":  7.5,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-26": {
            "label":   "Saturday | Pre-Long Run Priming Shakeout",
            "session": "4.0 km Zone 1 Easy Shakeout (<148 bpm) + Mobility & Core",
            "detail":  "Short, effortless shakeout to keep legs loose. Hydrate and eat high carbohydrates (rice/sweet potato) to fully top off glycogen for Sunday's 24k.",
            "run_km":  4.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-27": {
            "label":   "Sunday | Build II Milestone Long Run (24K)",
            "session": "24.0 km Progressive Aerobic Long Run (Zone 2, 162–172 bpm)",
            "detail":  "The cornerstone endurance anchor of Build II. Push 4 km beyond last week's 20k milestone. Full race nutrition simulation: take 3–4 gels at Km 7, 13, 18 with water/electrolytes.",
            "run_km":  24.0,
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
