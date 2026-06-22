# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# It must be updated every Sunday when a new week is planned.
# ANY agent or script that plans daily training MUST read this file first.
# Do NOT rely on chat memory or conversation history for the weekly plan.

week_start = "2026-06-22"
week_end   = "2026-06-28"
generated  = "2026-06-22"

plan = {
    "meta": {
        "week":        "June 22 – June 28, 2026",
        "phase":       "Base Rebuild (Marathon Prep) | Race: Capas Marathon TBD ~Nov 30",
        "load_target": "42–45 km running",
        "objective":   "First official week of the Base Rebuild phase using the new treadmill-heavy weekday structure. Long run steps up to 18 km.",
        "acwr_context":"[KIAT ENGINE ALERT] ACWR spiked to 2.180 (Danger Zone) due to the June volume cut lowering chronic load to 21 km/wk. Auto Speed Veto is ACTIVE.",
        "zone_update": "Zone 2 ceiling: 174 bpm. Zone 1 cap: 161 bpm.",
        "injury_note": "Achilles Insurance is MANDATORY on every leg day: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric phase.",
        "wrist_note":  "Right wrist injury as of June 16. Avoid push movements (bench, push-ups, dips). Pull movements cleared.",
        "marathon_note": "See marathon_plan.py for 26-week block structure, long run progression, and weight targets.",
    },
    "days": {
        "2026-06-22": {
            "label":   "Monday | ACTIVE RECOVERY (KIAT ENGINE VETO)",
            "session": "Complete Rest or Light Non-Impact Mobility",
            "detail":  "Kiat Engine AUTO VETO: Your ACWR is 2.180 (Danger) and EPOC is 79.4 mL/kg (Major). The planned 8-10 km treadmill run is CANCELLED. Do not run today.",
            "run_km":  0,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-23": {
            "label":   "Tuesday | Quality Session + Upper Body",
            "session": "Gym — Upper Body (Pull only) + 8 km Quality Run (Treadmill)",
            "detail":  "Gym: Pull movements only due to wrist injury. Run: 8 km total, including a 3-4 km tempo or fartlek block in the middle. Let HR rise into Z3/Z4 during the quality portion.",
            "run_km":  8,
            "gym":     True,
            "plyo":    False,
        },
        "2026-06-24": {
            "label":   "Wednesday | Easy Aerobic",
            "session": "7–9 km Easy Aerobic (Treadmill, 1.5–2% incline)",
            "detail":  "Recovery focused aerobic run. HR in Zone 1. Keep it light and easy.",
            "run_km":  8,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-25": {
            "label":   "Thursday | Legs + Core (Base)",
            "session": "Gym — Legs + Core",
            "detail":  "Base leg day (Leg press, hamstring curls, core). No heavy plyometrics. ACHILLES INSURANCE MANDATORY: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-06-26": {
            "label":   "Friday | Rest or Active Recovery",
            "session": "Complete Rest or 0–5 km Very Short Easy",
            "detail":  "Listen to your legs. If feeling fatigued, take complete rest. Otherwise, a very slow 5 km shakeout on the treadmill is fine.",
            "run_km":  0,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-27": {
            "label":   "Saturday | Pre-Fatigue Protocol (Moderate Legs + Core)",
            "session": "Gym — Legs + Core (Light/Moderate)",
            "detail":  "Pre-loading quads and hamstrings for Sunday long run. Moderate weight only. ACHILLES INSURANCE MANDATORY: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-06-28": {
            "label":   "Sunday | The Long Run",
            "session": "18 km Zone 2 Long Run (OUTSIDE)",
            "detail":  "Outside is MANDATORY for heat adaptation and terrain. Zone 2 effort, HR cap: 174 bpm (180 bpm if heat index is high).",
            "run_km":  18,
            "gym":     False,
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
    print(f"Zones:    {plan['meta']['zone_update']}")
    print(f"Achilles: {plan['meta']['injury_note']}")
    print(f"Wrist:    {plan['meta']['wrist_note']}")
    print()
    if today in plan["days"]:
        d = plan["days"][today]
        print(f"TODAY ({today}):")
        print(f"  {d['label']}")
        print(f"  Session: {d['session']}")
        print(f"  Detail:  {d['detail']}")
        print(f"  Run km target: {d['run_km']} km")
        print(f"  Gym: {d['gym']} | Plyo: {d['plyo']}")
    else:
        print(f"No plan entry found for today ({today}).")
        print("Full week:")
        for dt, d in plan["days"].items():
            print(f"  {dt}: {d['label']} — {d['session']}")
