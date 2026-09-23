import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# 1. Unschedule old Friday, Saturday, Sunday workouts
items_to_unschedule = [
    (1784570181, "Old Friday Strides"),
    (1787171041, "Old Friday 5.5k"),
    (1784566255, "Old Saturday Shakeout"),
    (1784566496, "Old Sunday Long Run")
]

for item_id, label in items_to_unschedule:
    try:
        client.unschedule_workout(item_id)
        print(f"[OK] Unscheduled {label} (CalendarItemID: {item_id})")
    except Exception as e:
        print(f"[NOTE] Could not unschedule {label} ({item_id}): {e}")

# Condition helpers
_TIME = lambda secs: {"conditionTypeId": 2, "conditionTypeKey": "time", "conditionValue": secs, "conditionValueType": None}
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

# ==========================================
# THU SEP 24: MARIKINA INDOOR BIKE FLUSH (35M)
# ==========================================
w_thu_bike = {
    "workoutName": "W14D4: Marikina Indoor Bike Flush [35m]",
    "description": "Active recovery spin in Marikina: 35m light spinning (80-90 rpm, low resistance). Zone 1 (<125 bpm). Flushes calves and quads with 0.0 ground reaction force.",
    "sportType": {"sportTypeId": 2, "sportTypeKey": "cycling"},
    "estimatedDurationInSecs": 2100,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 2, "sportTypeKey": "cycling"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _TIME(300), "5m Easy Spin Warmup (<115 bpm)", _hr_target(90, 115)),
            make_step(2, "interval", 3, _TIME(1500), "25m Smooth Cadence Flush (85-90 rpm, <125 bpm)", _hr_target(100, 125)),
            make_step(3, "cooldown", 2, _TIME(300), "5m Easy Spin Cooldown (<110 bpm)", _hr_target(90, 110))
        ]
    }]
}
res_bike = client.upload_workout(w_thu_bike)
wid_bike = res_bike.get("workoutId")
client.schedule_workout(wid_bike, "2026-09-24")
print(f"[OK] Scheduled Thursday Bike Flush (ID: {wid_bike}) for 2026-09-24")

# ==========================================
# FRI SEP 25: PRE-LONG RUN PRIMING SHAKEOUT (4K)
# ==========================================
w_fri_shakeout = {
    "workoutName": "W14D5: Pre-Long Run Priming Shakeout [4K]",
    "description": "Pre-Long Run Priming Shakeout: 4.0 km easy flat cruise (<148 bpm, Zone 1). Effortless turnover. Keep legs fresh for Saturday's 21k long run. Hydrate and carb-load today!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "interval", 3, _DIST(4000), "4.0 km Flat Easy Shakeout (<148 bpm)", _hr_target(130, 148))
        ]
    }]
}
res_fri = client.upload_workout(w_fri_shakeout)
wid_fri = res_fri.get("workoutId")
client.schedule_workout(wid_fri, "2026-09-25")
print(f"[OK] Scheduled Friday Pre-Long Run Shakeout (ID: {wid_fri}) for 2026-09-25")

# ==========================================
# SAT SEP 26: BUILD II MILESTONE LONG RUN (21K)
# ==========================================
w_sat_lr = {
    "workoutName": "W14D6: Build II Milestone Long Run [21K]",
    "description": "Build II Milestone Long Run: 21.0 km progressive aerobic run (Zone 2, 162-172 bpm). Flat route (Marikina Riverbanks / flat road). Mandatory fueling practice: Take 3 energy gels at Km 7, 13, and 18 with water!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 7200,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(2000), "2.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
            make_step(2, "interval", 3, _DIST(18000), "18.0 km Steady Zone 2 (Gels at Km 7, 13, 18)", _hr_target(162, 172)),
            make_step(3, "cooldown", 2, _DIST(1000), "1.0 km Cooldown Walk/Jog", _hr_target(130, 150))
        ]
    }]
}
res_sat = client.upload_workout(w_sat_lr)
wid_sat = res_sat.get("workoutId")
client.schedule_workout(wid_sat, "2026-09-26")
print(f"[OK] Scheduled Saturday Long Run (ID: {wid_sat}) for 2026-09-26")

# ==========================================
# SUN SEP 27: POST-LONG RUN RECOVERY FLUSH (4K / SPIN)
# ==========================================
w_sun_rec = {
    "workoutName": "W14D7: Post-Long Run Recovery Flush [4K]",
    "description": "Post-Long Run Active Recovery: 3.5 - 4.0 km very easy recovery jog (<145 bpm) or 30m spin / rest. Flush metabolic waste from Saturday's 21k!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "interval", 3, _DIST(4000), "4.0 km Very Easy Recovery Flush (<145 bpm)", _hr_target(125, 145))
        ]
    }]
}
res_sun = client.upload_workout(w_sun_rec)
wid_sun = res_sun.get("workoutId")
client.schedule_workout(wid_sun, "2026-09-27")
print(f"[OK] Scheduled Sunday Recovery Flush (ID: {wid_sun}) for 2026-09-27")

