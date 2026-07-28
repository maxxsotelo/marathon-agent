import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

saturday = "2026-07-25"
sunday = "2026-07-26"

_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
_DIST = lambda m: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": m, "conditionValueType": None}
_HR_Z2 = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "targetValueOne": 2, "targetValueTwo": 2}

# --- SATURDAY LEGS ---
sat_legs = {
    "workoutName": "Pre-Fatigue Legs (60-70% Cap)",
    "description": "60-70% max load. NO FAILURE SETS. Seated calf raises are the only exception (full load, 3s eccentric). Save the legs for the run tonight.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "training"},
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 5, "sportTypeKey": "training"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 1, "stepTypeKey": "warmup"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Warmup (Mobility)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Leg Press / Squats (60-70% load, no failure)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 3,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Seated Calf Raises (4x20 @ 70kg, 3s eccentric)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 4,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown (Press LAP to finish)"
                }
            ]
        }
    ]
}

# --- SATURDAY RUN ---
sat_run = {
    "workoutName": "7km Post-Legs Aerobic Flush",
    "description": "Run at night after leg day. This is the true pre-fatigue stimulus. Keep it strictly in Zone 2.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDistanceInMeters": 7000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _DIST(7000),
                    "endConditionValue": 7000,
                    "targetType": _HR_Z2,
                    "description": "7km Zone 2 on fatigued legs"
                }
            ]
        }
    ]
}

# --- SUNDAY LONG RUN ---
sun_run = {
    "workoutName": "18-20km Long Run (Step-down)",
    "description": "Week 5 Long Run (Step-down week). Route: Marikina Riverbank / Flat loop. Zone 2.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDistanceInMeters": 18000,
    "workoutSegments": [
        {
            "segmentOrder": 1,
            "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
            "workoutSteps": [
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 1,
                    "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                    "endCondition": _DIST(18000),
                    "endConditionValue": 18000,
                    "targetType": _HR_Z2,
                    "description": "18km Zone 2 Long Run (Keep going if you feel good)"
                },
                {
                    "type": "ExecutableStepDTO",
                    "stepOrder": 2,
                    "stepType": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
                    "endCondition": _LAP,
                    "targetType": _NO_TARGET,
                    "description": "Cooldown walk"
                }
            ]
        }
    ]
}

for w, date_str in [(sat_legs, saturday), (sat_run, saturday), (sun_run, sunday)]:
    try:
        res = client.upload_workout(w)
        wid = res.get("workoutId")
        client.schedule_workout(wid, date_str)
        print(f"[OK] Scheduled: {w['workoutName']} for {date_str}")
    except Exception as e:
        print(f"[ERR] Error scheduling {w['workoutName']}: {e}")
