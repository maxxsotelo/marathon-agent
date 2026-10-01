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
            "description": "Rest (45s, Press LAP when ready)"
        }
    ]

fri_gym_steps = []
ex_o = 1

# 1. Banded Terminal Knee Extensions (TKEs for VMO) - 3 sets x 15 reps
for s in range(3):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Banded TKEs (VMO Knee Activation) - Set {s+1}/3"))
    ex_o += 1

# 2. Glute Bridge Iso-Holds - 3 sets x 30s
for s in range(3):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Glute Bridge Iso-Holds (Pre-Run Activation) - Set {s+1}/3"))
    ex_o += 1

# 3. Light Cable Chest Crossovers / DB Pump - 3 sets x 12 reps (RPE 6 light)
for s in range(3):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Light Cable Flyes / Chest Pump (RPE 6) - Set {s+1}/3"))
    ex_o += 1

# 4. Lat Pulls / Dead Hangs (Spinal Decompression) - 3 sets x 45s
for s in range(3):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Bar Dead Hangs (Spinal Decompression) - Set {s+1}/3"))
    ex_o += 1

# 5. Core Planks & Outer Quad Foam Rolling - 3 sets
for s in range(3):
    fri_gym_steps.extend(make_strength_step(ex_o, f"Plank Hold (45s) & Quad Roll - Set {s+1}/3"))
    ex_o += 1

w_fri_gym = {
    "workoutName": "W15D5: Pre-Long Run Priming & Mobility [25m]",
    "description": "Pre-Long Run Gym Priming: VMO knee TKEs, glute activation, bar dead hangs (spinal decompression), light chest flyes (RPE 6), planks, and quad foam rolling. ZERO LEG WEIGHT LIFTING.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": fri_gym_steps
    }]
}

print("Uploading and scheduling Friday Priming Gym workout...")
try:
    res = client.upload_workout(w_fri_gym)
    wid = res.get("workoutId")
    client.schedule_workout(wid, "2026-10-02")
    print(f"[OK] Scheduled 'W15D5: Pre-Long Run Priming & Mobility' (ID: {wid}) for 2026-10-02!")
except Exception as e:
    print(f"[ERR] Failed: {e}")
