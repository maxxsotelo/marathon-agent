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

fri_gym_steps = []
ex_o = 1

# 1. DB Bench Press / Incline DB Press - 4 sets x 8-10 reps (RPE 8)
for s in range(4):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Incline DB Chest Press - Set {s+1}/4 (RPE 8.0)"))
    ex_o += 1

# 2. Incline DB Bicep Curls / Hammer Curls - 4 sets x 10-12 reps (RPE 8.5)
for s in range(4):
    fri_gym_steps.extend(make_strength_step(ex_o, f"DB Hammer Curls (Bicep/Brachialis Pump) - Set {s+1}/4"))
    ex_o += 1

# 3. Overhead Cable Tricep Extensions - 4 sets x 10-12 reps (RPE 8.5)
for s in range(4):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Overhead Cable Tricep Extensions - Set {s+1}/4"))
    ex_o += 1

# 4. DB Lateral Raises (Drop Sets) - 4 sets x 12-15 reps (RPE 8.5)
for s in range(4):
    fri_gym_steps.extend(make_strength_step(ex_o, f"DB Lateral Raises (Shoulder Pump) - Set {s+1}/4"))
    ex_o += 1

# 5. Hanging Leg Raises / Cable Crunch - 4 sets x 12-15 reps (Near Failure)
for s in range(4):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Hanging Leg Raises / Cable Crunch - Set {s+1}/4"))
    ex_o += 1

w_fri_gym = {
    "workoutName": "W15D5: Upper Hypertrophy & Arm/Chest Pump [45m]",
    "description": "Friday Hard Upper Hypertrophy: Incline DB Press, DB Hammer Curls, Overhead Tricep Extensions, DB Lateral Raises, Hanging Leg Raises. ZERO LEG LOADING (Legs reserved 100% for Saturday 16k LR).",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2700,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": fri_gym_steps
    }]
}

print("Uploading and scheduling Hard Upper Hypertrophy workout for Friday...")
try:
    res = client.upload_workout(w_fri_gym)
    wid = res.get("workoutId")
    client.schedule_workout(wid, "2026-10-02")
    print(f"[OK] Scheduled 'W15D5: Upper Hypertrophy & Arm/Chest Pump' (ID: {wid}) for 2026-10-02!")
except Exception as e:
    print(f"[ERR] Failed: {e}")
