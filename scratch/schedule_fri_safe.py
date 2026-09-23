import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

_DIST = lambda meters: {"conditionTypeId": 3, "conditionTypeKey": "distance", "conditionValue": meters, "conditionValueType": None}
_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}

def _hr_target(low_bpm, high_bpm):
    return {
        "workoutTargetTypeId": 4,
        "workoutTargetTypeKey": "heart.rate.zone",
        "displayOrder": 5,
        "targetValueOne": low_bpm,
        "targetValueTwo": high_bpm
    }

def make_step(step_order, step_type_key, step_type_id, condition, description, target=None):
    step = {
        "type": "ExecutableStepDTO",
        "stepOrder": step_order,
        "stepType": {"stepTypeId": step_type_id, "stepTypeKey": step_type_key, "displayOrder": step_type_id},
        "endCondition": condition,
        "endConditionValue": condition.get("conditionValue"),
        "description": description,
    }
    if target and target.get("workoutTargetTypeId") == 4:
        step["targetType"] = {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 5}
        step["targetValueOne"] = target["targetValueOne"]
        step["targetValueTwo"] = target["targetValueTwo"]
    else:
        step["targetType"] = _NO_TARGET
    return step

fri_safe_steps = [
    make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<150 bpm)", _hr_target(130, 150)),
    make_step(2, "interval", 3, _DIST(4000), "4.0 km Flat Easy Cruise (0% incline, <155 bpm)", _hr_target(140, 155)),
    make_step(3, "cooldown", 2, _DIST(500), "500m Cooldown Walk/Jog (<145 bpm)", _hr_target(130, 145))
]

w_fri_safe = {
    "workoutName": "W14D5: Flat Aerobic Cruise [5.5K] (Calf Safe)",
    "description": "Adjusted calf-safe aerobic cruise: 5.5 km flat on treadmill (0.0% or 0.5% incline, NO HILLS). Strides VETOED to protect right calf. Keep HR < 155 bpm.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 2000,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": fri_safe_steps
    }]
}

target_date = "2026-09-25"
print("Uploading and scheduling calf-safe Friday workout...")
res = client.upload_workout(w_fri_safe)
wid = res.get("workoutId")
client.schedule_workout(wid, target_date)
print(f"[OK] Successfully scheduled Calf-Safe Friday Workout (ID: {wid}) for {target_date}!")

