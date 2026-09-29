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
            "description": "Rest (45-60s, Press LAP when ready)"
        }
    ]

wed_gym_steps = []
ex_o = 1

# 1. Cable Woodchoppers / Core Rotational - 3 sets x 12-15 reps
for s in range(3):
    wed_gym_steps.extend(make_strength_step(ex_o, f"Cable Rotational Woodchoppers - Set {s+1}/3"))
    ex_o += 1

# 2. Captain's Chair / Hanging Leg Raises - 3 sets x 12-15 reps
for s in range(3):
    wed_gym_steps.extend(make_strength_step(ex_o, f"Hanging Leg Raises / Knee Tucks - Set {s+1}/3"))
    ex_o += 1

# 3. Cable Face Pulls & Rotator Cuff External Rotations - 3 sets x 15 reps
for s in range(3):
    wed_gym_steps.extend(make_strength_step(ex_o, f"Rotator Cuff External Rotations (Cable/DB) - Set {s+1}/3"))
    ex_o += 1

# 4. Dumbbell Forearm Wrist Curls & Reverse Curls - 3 sets x 15 reps
for s in range(3):
    wed_gym_steps.extend(make_strength_step(ex_o, f"Wrist Curls & Reverse Wrist Curls - Set {s+1}/3"))
    ex_o += 1

# 5. Abdominal Planks / Side Planks - 3 sets x 45-60s
for s in range(3):
    wed_gym_steps.extend(make_strength_step(ex_o, f"Abdominal Side Planks - Set {s+1}/3"))
    ex_o += 1

w_wed_gym = {
    "workoutName": "W15D3: Core, Prehab & Grip Conditioning [AF Taft]",
    "description": "Complementary gym conditioning for Wednesday: Rotational core, hanging leg raises, rotator cuff prehab, forearms/grip, side planks. Preserves 100% of upper back/biceps for Thursday Pull!",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 1800,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": wed_gym_steps
    }]
}

print("Uploading and scheduling Wednesday Core & Prehab workout...")
try:
    res = client.upload_workout(w_wed_gym)
    wid = res.get("workoutId")
    client.schedule_workout(wid, "2026-09-30")
    print(f"[OK] Scheduled 'W15D3: Core, Prehab & Grip Conditioning' (ID: {wid}) for 2026-09-30!")
except Exception as e:
    print(f"[ERR] Failed: {e}")
