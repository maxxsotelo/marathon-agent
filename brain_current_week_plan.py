# CURRENT WEEKLY PLAN
# This file is the single source of truth for the active training week.
# It must be updated every Sunday when a new week is planned.
# ANY agent or script that plans daily training MUST read this file first.
# Do NOT rely on chat memory or conversation history for the weekly plan.

week_start = "2026-06-29"
week_end   = "2026-07-05"
generated  = "2026-06-29"

plan = {
    "meta": {
        "week":        "June 29 – July 5, 2026",
        "phase":       "Base Rebuild (Marathon Prep) | Week 2/6",
        "load_target": "45–48 km running",
        "objective":   "Week 2 of Base Rebuild. Consolidate the 18km long run, push to 19-20km this weekend. Increase aerobic volume slightly while maintaining strict Z2 discipline.",
        "acwr_context":"ACWR is well balanced. Last week was a high-volume peak (+10.7% WoW). Focus on smooth volume accumulation this week.",
        "zone_update": "Zone 2 ceiling: 174 bpm. Zone 1 cap: 161 bpm.",
        "injury_note": "Achilles bulletproofing (4x20 Seated Calf Raises @ 70 kg) recommended on leg days.",
        "wrist_note":  "Right wrist TFCC tear healed. Normal Push and boxing training cleared, but use dedicated wrist support for impact.",
        "marathon_note": "See brain_marathon_plan.py for 26-week block structure.",
    },
    "days": {
        "2026-06-29": {
            "label":   "Monday | Easy Aerobic Base + Strides",
            "session": "8–10 km Easy Aerobic (Outside) + 4-6x Strides",
            "detail":  "Aerobic base building. Keep HR in Zone 2 (162–174 bpm). Finish the run with 4 to 6 sets of 20-second strides to engage fast-twitch fibers (walk/jog recovery between each).",
            "run_km":  9,
            "gym":     False,
            "plyo":    False,
        },
        "2026-06-30": {
            "label":   "Tuesday | Home Upper Body (Run Postponed)",
            "session": "Home — Upper Body (Pull/Core only)",
            "detail":  "Home Workout (AM): Pull and core movements only. Quality Run was postponed to Wednesday due to low energy.",
            "run_km":  0,
            "gym":     False,
            "plyo":    False,
        },
        "2026-07-01": {
            "label":   "Wednesday | Quality Session (Tempo)",
            "session": "8-10 km Quality Run (Outside)",
            "detail":  "Rescheduled from Tuesday. 8-10 km total, including a 4 km tempo block. Let HR rise into Z3/Z4 during the quality portion.",
            "run_km":  9,
            "gym":     False,
            "plyo":    False,
        },
        "2026-07-02": {
            "label":   "Thursday | Legs + Core (Wrist-Safe)",
            "session": "Gym — Legs + Core",
            "detail":  "Shifted from Wednesday. Base leg day (Leg press, stability ball hamstring curls, core circuit, 70kg seated calf raises). No plyometrics.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-07-03": {
            "label":   "Friday | Zone 2 Aerobic",
            "session": "8–10 km Zone 2 Aerobic (Outside)",
            "detail":  "Shifted from Thursday. Steady Zone 2 (162-174 bpm). Strict HR cap. Focus on cadence ~175spm.",
            "run_km":  9,
            "gym":     False,
            "plyo":    False,
        },
        "2026-07-04": {
            "label":   "Saturday | Pre-Fatigue Protocol",
            "session": "Gym — Legs + Core (Light/Moderate)",
            "detail":  "Light pre-fatigue session. Focus on mobility, core stability, and Achilles bulletproofing. Don't fry the quads.",
            "run_km":  0,
            "gym":     True,
            "plyo":    False,
        },
        "2026-07-05": {
            "label":   "Sunday | The Long Run",
            "session": "19-20 km Zone 2 Long Run (OUTSIDE)",
            "detail":  "The weekend long run. Strict pacing and fueling practice. Target 19-20km entirely in Z2 (162-174 bpm).",
            "run_km":  19.5,
            "gym":     False,
            "plyo":    False,
        }
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
