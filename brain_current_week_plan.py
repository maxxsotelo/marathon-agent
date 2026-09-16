# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# Updated for Week 13 (Sep 14 - Sep 20, 2026) - BUILD II BRIDGE (BSP Onboarding & AF Taft Integration)

week_start = "2026-09-14"
week_end   = "2026-09-20"
generated  = "2026-09-15"

plan = {
    "meta": {
        "week":        "September 14 – September 20, 2026",
        "phase":       "Build II Bridge | Week 13 (BSP Onboarding & AF Taft Integration)",
        "load_target": "45–48 km | Long Run: 18.0–20.0 km",
        "objective":   "Seamlessly adapt training to new life at Bangko Sentral ng Pilipinas (BSP), new condo, and newly unlocked 1-year Anytime Fitness Taft membership. Maintain threshold speed reserve, integrate condo pool, and bank 47 km volume with optimal 1.12 ACWR.",
        "acwr_context":"ACWR is optimal at 1.12. Morning vitals pristine (Body Battery 92, RHR 40 bpm).",
        "zone_update": "Zone 2 ceiling: 174 bpm (floor 162 bpm). LTHR: 196 bpm. Max HR: 206 bpm.",
        "injury_note": "Zero structural symptoms. Use Adidas EVO SL for road runs, Boston 12s for treadmill or rain.",
        "facility_note":"New facilities: Anytime Fitness Taft (1-yr membership confirmed), Condo Pool (closed Mon), and BSP Employee Gym.",
    },
    "days": {
        "2026-09-14": {
            "label":   "Monday | Day 1 at BSP + AF Taft Test Run",
            "session": "3.00 km Treadmill @ 5:32/km (Avg HR 145, TE 2.2) + Malate Walking",
            "detail":  "Day 1 at BSP completed. Acquired 1-yr Anytime Fitness Taft membership and logged 3k shakeout + 16,394 steps. Completed.",
            "run_km":  3.0,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-15": {
            "label":   "Tuesday | Treadmill Hills & Heavy Pulling Double",
            "session": "6.29 km Treadmill (5:19/km, 1.3k of 2-7% hills, HR 155, TE 3.2) + 38m Upper Pulling",
            "detail":  "6.29 km cruise at AF Taft + heavy lat pulldowns, seated cable rows, face pulls, lateral raises. 18,735 steps, 1,030 active kcal. Completed.",
            "run_km":  6.29,
            "gym":     True,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-16": {
            "label":   "Wednesday | Quality Threshold Anchor",
            "session": "8.0 km Total (2k WU + 4x1,000m Threshold @ 14.0-14.6 km/h + 2k CD)",
            "detail":  "Sharpen sub-3:00 speed reserve at AF Taft or outdoor loop. 90s float recovery between reps. Fast-twitch maintenance.",
            "run_km":  8.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-17": {
            "label":   "Thursday | Inaugural Condo Pool Flush + Strength",
            "session": "30–40m Zero-Impact Pool Swim / Hydrotherapy + Upper Body Strength",
            "detail":  "First deployment of the condo pool! Hydrostatic compression flushes calves/Achilles. Upper body push/pull at AF Taft or BSP gym.",
            "run_km":  0.0,
            "gym":     True,
            "pool":    True,
            "plyo":    False,
        },
        "2026-09-18": {
            "label":   "Friday | Aerobic Foundation Cruise",
            "session": "6.0 – 7.0 km Zone 2 Aerobic Cruise (162–172 bpm)",
            "detail":  "Cap off your first week at the BSP with smooth aerobic miles. Relaxed mental reset.",
            "run_km":  6.5,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-19": {
            "label":   "Saturday | Pre-Long Run Shakeout",
            "session": "4.5 – 5.0 km Zone 1 Easy (<150 bpm) + 4x100m Light Strides",
            "detail":  "Short neuromuscular turnover. Carb load and hydrate for Sunday's anchor long run.",
            "run_km":  5.0,
            "gym":     False,
            "pool":    False,
            "plyo":    False,
        },
        "2026-09-20": {
            "label":   "Sunday | Aerobic Endurance Long Run",
            "session": "18.0 – 20.0 km Steady Zone 2 Long Run",
            "detail":  "The settled endurance anchor now that Week 1 is in the books! In-run fueling practice (gels and electrolytes).",
            "run_km":  19.0,
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
