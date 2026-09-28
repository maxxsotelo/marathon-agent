import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}

def make_strength_step(order, name):
    return [
        {
            "type": "ExecutableStepDTO",
            "stepOrder": order * 2 - 1,
            "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
            "endCondition": _LAP,
            "targetType": _NO_TARGET,
            "description": name
        },
        {
            "type": "ExecutableStepDTO",
            "stepOrder": order * 2,
            "stepType": {"stepTypeId": 5, "stepTypeKey": "rest"},
            "endCondition": _LAP,
            "targetType": _NO_TARGET,
            "description": "Rest (60-90s, Press LAP when ready)"
        }
    ]

push_steps = []
ex_o = 1
# 1. Seated Chest Press (Machine / DB) - 4 sets x 8-12 reps
for s in range(4):
    push_steps.extend(make_strength_step(ex_o, f"Seated Machine Chest Press - Set {s+1}/4 (RPE 7-8)"))
    ex_o += 1

# 2. Incline DB Bench Press - 3 sets x 10-12 reps
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Incline Dumbbell Bench Press - Set {s+1}/3 (RPE 7-8)"))
    ex_o += 1

# 3. Cable Tricep Pushdowns (Rope / V-Bar) - 4 sets x 12-15 reps
for s in range(4):
    push_steps.extend(make_strength_step(ex_o, f"Cable Tricep Rope Pushdowns - Set {s+1}/4 (RPE 8)"))
    ex_o += 1

# 4. DB Lateral Raises - 3 sets x 12-15 reps
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Seated / Standing DB Lateral Raises - Set {s+1}/3 (RPE 8)"))
    ex_o += 1

# 5. Core: Hanging Leg Raises / Ab Planks - 3 sets
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Ab Planks (60s) or Hanging Leg Raises - Set {s+1}/3"))
    ex_o += 1

w_mon_push = {
    "workoutName": "W15D1: Upper Push & Core [AF Taft]",
    "description": "Feasible upper body push hypertrophy & core stability for Monday post-21k. Seated Chest Press, Incline DB Press, Triceps, Lateral Raises, Planks. 0.0 LEG IMPACT.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2700,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": push_steps
    }]
}

print("Uploading and scheduling Monday Upper Push workout...")
try:
    res = client.upload_workout(w_mon_push)
    wid = res.get("workoutId")
    client.schedule_workout(wid, "2026-09-28")
    print(f"[OK] Scheduled 'W15D1: Upper Push & Core' (ID: {wid}) for 2026-09-28!")
except Exception as e:
    print(f"[ERR] Failed: {e}")
