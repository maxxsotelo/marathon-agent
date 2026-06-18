# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# It must be updated every Sunday when a new week is planned.
# ANY agent or script that plans daily training MUST read this file first.
# Do NOT rely on chat memory or conversation history for the weekly plan.

week_start = "2026-06-15"
week_end   = "2026-06-21"
generated  = "2026-06-15"  # Date this plan was created

plan = {
    "meta": {
        "week":        "June 15 – June 21, 2026",
        "phase":       "Perpetual Base / Efficiency Protocol (No Race Date)",
        "load_target": "30–32 km running",
        "objective":   "Solidify aerobic base at new LTHR zones. Hold volume steady (post-high-load week). ACWR target: 0.9–1.15.",
        "acwr_context":"Prior acute load was 40.4 km. This week deliberately absorbs that work.",
        "zone_update": "New Zone 2 ceiling: 174 bpm (LTHR method, updated June 6 2026). Zone 1 cap: 162 bpm.",
        "injury_note": "Achilles Insurance is MANDATORY on every leg day: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric phase.",
        "wrist_note":  "Right wrist injury as of June 16. Avoid push movements (bench, push-ups, dips). Pull movements cleared.",
    },
    "days": {
        "2026-06-15": {
            "label":   "Monday | Active Recovery",
            "session": "Complete Rest or Light Mobility",
            "detail":  "Let the 15 km long run from Sunday fully absorb into the legs. Eat slightly below maintenance.",
            "run_km":  0,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-16": {
            "label":   "Tuesday | Upper Body (Push/Pull)",
            "session": "Gym — Upper Body",
            "detail":  "Standard heavy Push/Pull block. Push movements to be skipped or modified due to wrist injury. Pull movements cleared. Keep protein high.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-06-17": {
            "label":   "Wednesday | Speed Work (Speed Reserve)",
            "session": "6–8 km Fartlek or Strides (Santa Elena or UP)",
            "detail":  "5x 1-minute surges at 3:55–4:10/km pace (sub-3 marathon speed reserve). First 1 km warmup MUST be under 130 bpm. Let HR climb into Zone 4/5 during surges.",
            "run_km":  7,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-18": {
            "label":   "Thursday | Legs + Core (Base)",
            "session": "Gym — Legs + Core",
            "detail":  "Leg Press (120 kg+), Hamstring Curls, Core circuit. NO heavy plyometrics today — this is a base/volume leg day. ACHILLES INSURANCE MANDATORY: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,  # Thursday is BASE legs, NOT the plyometric day
        },
        "2026-06-19": {
            "label":   "Friday | Zone 2 Easy Run",
            "session": "8–10 km Zone 2 (Concepcion Uno)",
            "detail":  "Aerobic flush. HR ceiling: 174 bpm (new Zone 2). Tired Legs Protocol: if legs feel heavy, let pace drop. If loose, allow down to 6:00/km as long as HR stays under 174 bpm.",
            "run_km":  9,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-20": {
            "label":   "Saturday | Pre-Fatigue Protocol (Moderate Legs + Core)",
            "session": "Gym — Legs + Core (Light/Moderate)",
            "detail":  "Pre-loading quads and hamstrings for Sunday long run. Moderate weight only. ACHILLES INSURANCE MANDATORY: 4x20 Seated Calf Raises @ 70 kg, 3s eccentric.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-06-21": {
            "label":   "Sunday | The Long Run",
            "session": "16–18 km Zone 2 Long Run",
            "detail":  "Accumulated Fatigue Protocol on pre-loaded legs from Saturday. Allow cadence to self-select. First km under 130 bpm. HR cap: 174 bpm (or 180 bpm if heat index >= 33 degrees C).",
            "run_km":  17,
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
