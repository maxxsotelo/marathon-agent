import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

# Condition helpers
_LAP = {"conditionTypeId": 1, "conditionTypeKey": "lap.button"}
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
            "description": "Rest (Press LAP when ready for next set)"
        }
    ]

workouts_to_schedule = []

# ==========================================
# MON SEP 28: RECOVERY SHAKEOUT / REST (4K)
# ==========================================
w_mon = {
    "workoutName": "W15D1: Post-21K Recovery Shakeout [4K]",
    "description": "Post-21K Active Recovery: 4.0 km very easy recovery jog (<145 bpm) or full rest. Flush remaining quad soreness. Effortless, light turnover.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "interval", 3, _DIST(4000), "4.0 km Very Easy Recovery Cruise (<145 bpm)", _hr_target(125, 145))
        ]
    }],
    "target_date": "2026-09-28"
}
workouts_to_schedule.append(w_mon)

# ==========================================
# TUE SEP 29: AEROBIC BASE CRUISE (6K) + PUSH
# ==========================================
w_tue_run = {
    "workoutName": "W15D2: Zone 2 Aerobic Cruise [6K]",
    "description": "Controlled aerobic base cruise. Lock into Zone 2 (162-172 bpm). Flat surface or treadmill (0% incline).",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 2100,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
            make_step(2, "interval", 3, _DIST(4500), "4.5 km Zone 2 Aerobic Cruise (162-172 bpm)", _hr_target(162, 172)),
            make_step(3, "cooldown", 2, _DIST(500), "500m Cooldown Walk/Jog", _hr_target(130, 150))
        ]
    }],
    "target_date": "2026-09-29"
}
workouts_to_schedule.append(w_tue_run)

push_steps = []
ex_o = 1
for s in range(4):
    push_steps.extend(make_strength_step(ex_o, f"Chest Press (Machine/DB) - Set {s+1}/4"))
    ex_o += 1
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Incline Dumbbell Press - Set {s+1}/3"))
    ex_o += 1
for s in range(4):
    push_steps.extend(make_strength_step(ex_o, f"Cable Tricep Pushdowns - Set {s+1}/4"))
    ex_o += 1
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Overhead Cable Extensions - Set {s+1}/3"))
    ex_o += 1
for s in range(3):
    push_steps.extend(make_strength_step(ex_o, f"Hanging Leg Raises / Planks - Set {s+1}/3"))
    ex_o += 1

w_tue_push = {
    "workoutName": "W15D2: Upper Push & Core [AF Taft]",
    "description": "Upper body push hypertrophy and core stability. Chest, triceps, anterior shoulders, planks. STRICT VETO ON LEGS.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": push_steps
    }],
    "target_date": "2026-09-29"
}
workouts_to_schedule.append(w_tue_push)

# ==========================================
# WED SEP 30: AEROBIC FOUNDATION + STRIDES (7.5K)
# ==========================================
wed_steps = [
    make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
    make_step(2, "interval", 3, _DIST(6000), "6.0 km Zone 2 Aerobic Cruise (162-172 bpm)", _hr_target(162, 172))
]
w_ord = 3
for rep in range(4):
    wed_steps.append(make_step(w_ord, "interval", 3, _DIST(100), f"Stride {rep+1}/4: 100m Fast Acceleration (~3:45-3:55/km)"))
    w_ord += 1
    wed_steps.append(make_step(w_ord, "recovery", 4, _DIST(100), f"Recovery {rep+1}/4: 100m Easy Walk/Jog"))
    w_ord += 1

wed_steps.append(make_step(w_ord, "cooldown", 2, _DIST(200), "200m Cooldown Walk", _hr_target(130, 150)))

w_wed = {
    "workoutName": "W15D3: Aerobic Foundation + Strides [7.5K]",
    "description": "Smooth Zone 2 aerobic volume followed by 4x100m relaxed strides. (Speed repeats canceled for leg muscle remodeling).",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 2700,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": wed_steps
    }],
    "target_date": "2026-09-30"
}
workouts_to_schedule.append(w_wed)

# ==========================================
# THU OCT 1: MARIKINA INDOOR BIKE FLUSH (35M) + PULL
# ==========================================
w_thu_bike = {
    "workoutName": "W15D4: Marikina Indoor Bike Flush [35m]",
    "description": "Active recovery spin in Marikina: 35m light spinning (85-90 rpm, low resistance, Zone 1 <125 bpm). 0.0 ground reaction force.",
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
    }],
    "target_date": "2026-10-01"
}
workouts_to_schedule.append(w_thu_bike)

pull_steps = []
ex_p = 1
for s in range(4):
    pull_steps.extend(make_strength_step(ex_p, f"Lat Pulldowns (Wide/Neutral) - Set {s+1}/4"))
    ex_p += 1
for s in range(4):
    pull_steps.extend(make_strength_step(ex_p, f"Seated Cable Rows - Set {s+1}/4"))
    ex_p += 1
for s in range(4):
    pull_steps.extend(make_strength_step(ex_p, f"Face Pulls (Rear Delts) - Set {s+1}/4"))
    ex_p += 1
for s in range(3):
    pull_steps.extend(make_strength_step(ex_p, f"Dumbbell Lateral Raises - Set {s+1}/3"))
    ex_p += 1
for s in range(3):
    pull_steps.extend(make_strength_step(ex_p, f"Ab Planks / Leg Raises - Set {s+1}/3"))
    ex_p += 1

w_thu_pull = {
    "workoutName": "W15D4: Upper Pull & Core [AF Taft / Marikina]",
    "description": "Posterior chain pulling strength: Lat pulldowns, seated cable rows, face pulls, lateral raises, and core. ZERO LEGS.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": pull_steps
    }],
    "target_date": "2026-10-01"
}
workouts_to_schedule.append(w_thu_pull)

# ==========================================
# FRI OCT 2: PRE-LONG RUN PRIMING SHAKEOUT (4K)
# ==========================================
w_fri_shakeout = {
    "workoutName": "W15D5: Pre-Long Run Priming Shakeout [4K]",
    "description": "Easy 4.0 km flat shakeout (<148 bpm, Zone 1) in Puma Velocity Nitro 3s. Effortless turnover. High carbohydrate loading today!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "interval", 3, _DIST(4000), "4.0 km Flat Easy Shakeout (<148 bpm)", _hr_target(130, 148))
        ]
    }],
    "target_date": "2026-10-02"
}
workouts_to_schedule.append(w_fri_shakeout)

# ==========================================
# SAT OCT 3: CUTBACK AEROBIC LONG RUN (16K)
# ==========================================
w_sat_lr = {
    "workoutName": "W15D6: Cutback Aerobic Long Run [16K]",
    "description": "Regulated Cutback Long Run: 16.0 km steady Zone 2 cruise (162-172 bpm). Flat route in Marikina. 30k deferred to Week 16 to allow quad & knee recovery. Take 2 gels at Km 6 and 12!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 5400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
            make_step(2, "interval", 3, _DIST(14000), "14.0 km Steady Zone 2 (Gels at Km 6, 12)", _hr_target(162, 172)),
            make_step(3, "cooldown", 2, _DIST(1000), "1.0 km Cooldown Walk/Jog", _hr_target(130, 150))
        ]
    }],
    "target_date": "2026-10-03"
}
workouts_to_schedule.append(w_sat_lr)

# UPLOAD AND SCHEDULE EACH
print(f"Uploading and scheduling {len(workouts_to_schedule)} workouts for Week 15...")
for w in workouts_to_schedule:
    t_date = w.pop("target_date")
    name = w["workoutName"]
    try:
        res = client.upload_workout(w)
        wid = res.get("workoutId")
        client.schedule_workout(wid, t_date)
        print(f"[OK] Scheduled '{name}' (ID: {wid}) for {t_date}")
    except Exception as e:
        print(f"[ERR] Failed to schedule '{name}' for {t_date}: {e}")

