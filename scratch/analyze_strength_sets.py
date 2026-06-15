import os, sys, json
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

activities = client.get_activities_by_date("2026-05-27", "2026-05-27")
strength_id = None
for act in activities:
    if act.get("activityType", {}).get("typeKey") == "strength_training":
        strength_id = act.get("activityId")
        break

sets = client.get_activity_exercise_sets(strength_id)
exercise_sets = sets.get("exerciseSets", [])

# Parse and summarize
active_sets = [s for s in exercise_sets if s.get("setType") == "ACTIVE"]
rest_sets   = [s for s in exercise_sets if s.get("setType") == "REST"]

# Group by exercise name
from collections import defaultdict
grouped = defaultdict(list)
for s in active_sets:
    exs = s.get("exercises", [])
    name = exs[0].get("name", "UNKNOWN") if exs else "UNKNOWN"
    cat  = exs[0].get("category", "UNKNOWN") if exs else "UNKNOWN"
    grouped[(cat, name)].append(s)

print("=" * 65)
print("STRENGTH SESSION BREAKDOWN — Loaded Diper (May 27, 2026)")
print("=" * 65)

total_reps  = 0
total_vol   = 0.0  # kg * reps (volume load)
set_count   = 0

for (cat, name), sets_list in grouped.items():
    label = (name or "Unknown").replace("_", " ").title()
    print(f"\n>> {label}  [{cat}]")
    print(f"   {'Set':<5} {'Reps':<8} {'Weight (kg)':<14} {'Duration':<12} {'Volume'}")
    print(f"   {'-'*4}  {'-'*6}  {'-'*12}  {'-'*10}  {'-'*10}")
    exercise_vol = 0.0
    exercise_reps = 0
    for i, s in enumerate(sets_list, 1):
        reps    = s.get("repetitionCount") or 0
        weight  = (s.get("weight") or 0) / 1000  # g → kg
        dur     = s.get("duration", 0)
        vol     = reps * weight
        exercise_vol  += vol
        exercise_reps += reps
        total_vol     += vol
        total_reps    += reps
        set_count     += 1
        weight_str = f"{weight:.1f} kg" if weight > 0 else "BW"
        vol_str    = f"{vol:.0f} kg" if weight > 0 else "-"
        dur_str    = f"{dur:.0f}s" if dur is not None else "N/A"
        print(f"   {i:<5} {reps:<8} {weight_str:<14} {dur_str:<12} {vol_str}")
    print(f"   -> Subtotal: {len(sets_list)} sets | {exercise_reps} reps | {exercise_vol:.0f} kg volume load")

# Rest analysis
rest_durations = [s.get("duration", 0) or 0 for s in rest_sets]
avg_rest = sum(rest_durations) / len(rest_durations) if rest_durations else 0

print("\n" + "=" * 65)
print("SESSION SUMMARY")
print("=" * 65)
print(f"  Total Active Sets:       {set_count}")
print(f"  Total Reps:              {total_reps}")
print(f"  Total Volume Load:       {total_vol:.0f} kg")
print(f"  Avg Rest Between Sets:   {avg_rest:.0f}s ({avg_rest/60:.1f} min)")
print(f"  Exercises Detected:      {len(grouped)}")
print(f"  Avg HR (session):        130 bpm")
print(f"  Max HR (session):        190 bpm")
print(f"  Duration:                51.9 min")
print(f"  Calories:                386 kcal")
