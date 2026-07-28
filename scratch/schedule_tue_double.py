import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from datetime import date

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
_DIST = lambda m: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": m, "conditionValueType": None}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
_HR_Z2 = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 2, "targetValueTwo": 2}

today = date.today().isoformat()

# --- SWIM ---
swim = {
    "workoutName": "Afternoon Swim Flush (1000-1500m)",
    "description": "Stop-and-go lengths. Warm up the legs before tonight's run. Relax and loosen up.",
    "sportType": {"sportTypeId": 4, "sportTypeKey": "lap_swimming"},
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 4, "sportTypeKey": "lap_swimming"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "1000-1500m stop-and-go (Press LAP to end)"
                }
            ]
        }
    ]
}

# --- ZONE 2 RUN ---
run = {
    "workoutName": "10-12km Zone 2 Aerobic Development",
    "description": "Week 5 Day 1. Full Zone 2 aerobic stimulus. 162-174 bpm. No surges, no strides. Just clean aerobic base work.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDistanceInMeters": 11000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _DIST(1000),
                    "endConditionValue": 1000,
                    "targetType": _NO_TARGET,
                    "description": "1km Warmup — keep HR under 140 bpm"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _DIST(10000),
                    "endConditionValue": 10000,
                    "targetType": _HR_Z2,
                    "description": "10km Zone 2 (162-174 bpm) — aerobic base development"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown walk/jog home (Press LAP to save)"
                }
            ]
        }
    ]
}

for name, workout in [("Swim", swim), ("Zone 2 Run", run)]:
    try:
        res = client.upload_workout(workout)
        wid = res.get("workoutId")
        client.schedule_workout(wid, today)
        print(f"[OK] Scheduled: {workout['workoutName']}")
    except Exception as e:
        print(f"[ERR] Error scheduling {name}: {e}")
