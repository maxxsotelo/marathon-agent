import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
_LAP  = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}

def work_step(order, name, secs):
    return {
        "type": "ExecutableStepDTO",
        "stepOrder": order,
        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
        "endCondition": _TIME(secs),
        "endConditionValue": secs,
        "targetType": _NO_TARGET,
        "description": name,
    }

def rest_step(order, secs):
    return {
        "type": "ExecutableStepDTO",
        "stepOrder": order,
        "stepType": {"stepTypeId": 5, "stepTypeKey": "rest"},
        "endCondition": _TIME(secs),
        "endConditionValue": secs,
        "targetType": _NO_TARGET,
        "description": "Rest / Breathe",
    }

def round_group(order, drill_name, work_secs=180, rest_secs=60):
    return {
        "type": "RepeatGroupDTO",
        "stepOrder": order,
        "stepType": {"stepTypeId": 6, "stepTypeKey": "repeat"},
        "numberOfIterations": 1,
        "workoutSteps": [
            work_step(1, drill_name, work_secs),
            rest_step(2, rest_secs),
        ]
    }

# 45-min structure:
# Warmup:   1x 5min shadow boxing
# Rounds:   9x (3min drill + 1min rest) = 36 min
# Cooldown: 1x 4min stretch
# Total:    45 min

drills = [
    "R1: Shadow Boxing — Footwork + Jab-Cross (1-2)",
    "R2: Jab-Cross Rapid Fire — Stay on toes, fast hands",
    "R3: Jab-Cross-Hook (1-2-3) — Rotate hips on the hook",
    "R4: Body Shots — Body jab + Body cross, low guard",
    "R5: Jab-Cross-Hook-Uppercut (1-2-3-4) — Full combo",
    "R6: Slip Left + Jab Counter / Slip Right + Cross Counter",
    "R7: Lead Hook + Rear Uppercut (3-4) — Inside fighting",
    "R8: Jab-Cross-Hook-Cross (1-2-3-2) — Signature combo",
    "R9: FREESTYLE — Max output, mix everything",
]

steps = []
i = 1

# Warmup
steps.append({
    "type": "ExecutableStepDTO",
    "stepOrder": i,
    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
    "endCondition": _TIME(300),
    "endConditionValue": 300,
    "targetType": _NO_TARGET,
    "description": "Warmup — Light shadow boxing, neck rolls, shoulder circles, wrist rotations",
})
i += 1

# 9 drill rounds
for drill in drills:
    steps.append(round_group(i, drill, work_secs=180, rest_secs=60))
    i += 1

# Cooldown
steps.append({
    "type": "ExecutableStepDTO",
    "stepOrder": i,
    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
    "endCondition": _TIME(240),
    "endConditionValue": 240,
    "targetType": _NO_TARGET,
    "description": "Cooldown — Shadow box at 20% intensity, deep breathing, stretch shoulders + wrists",
})

workout = {
    "workoutName": "Boxing Drills — 45min HIIT",
    "description": (
        "9-round structured boxing session. 3 min work / 1 min rest. "
        "Warmup 5min, Cooldown 4min. Focus on mechanics before power. "
        "Keep guard tight at all times. Wraps mandatory."
    ),
    "estimatedDurationInSecs": 2700,
    "sportType": {"sportTypeId": 26, "sportTypeKey": "hiit"},
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 26, "sportTypeKey": "hiit"},
            "workoutSteps": steps,
        }
    ],
}

today = date.today().isoformat()
print(f"Uploading 45min Boxing HIIT workout for {today}...")
try:
    res = client.upload_workout(workout)
    workout_id = res.get("workoutId")
    print(f"Uploaded! Workout ID: {workout_id}")
    client.schedule_workout(workout_id, today)
    print(f"Scheduled on Garmin for {today}!")
except Exception as e:
    print(f"Upload error: {e}")
    print("Trying alternate sport type...")
    workout["sportType"] = {"sportTypeId": 4, "sportTypeKey": "cardio"}
    workout["workoutSegments"][0]["sportType"] = {"sportTypeId": 4, "sportTypeKey": "cardio"}
    try:
        res = client.upload_workout(workout)
        workout_id = res.get("workoutId")
        print(f"Uploaded as Cardio! Workout ID: {workout_id}")
        client.schedule_workout(workout_id, today)
        print(f"Scheduled on Garmin for {today}!")
    except Exception as e2:
        print(f"Second attempt error: {e2}")
