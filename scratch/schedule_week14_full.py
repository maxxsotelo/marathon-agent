import os, sys
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
# MON SEP 21: EASY RECOVERY SHAKEOUT (4K)
# ==========================================
w_mon = {
    "workoutName": "W14D1: Easy Recovery Shakeout [4K]",
    "description": "Active recovery shakeout run after big 20k weekend. Keep heart rate strictly below 150 bpm in Zone 1. Effortless, gentle turnover.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(500), "500m Easy Warmup", _hr_target(130, 150)),
            make_step(2, "interval", 3, _DIST(3000), "3.0 km Recovery Cruise (<150 bpm)", _hr_target(130, 150)),
            make_step(3, "cooldown", 2, _DIST(500), "500m Cooldown Jog/Walk", _hr_target(130, 145))
        ]
    }],
    "target_date": "2026-09-21"
}
workouts_to_schedule.append(w_mon)

# ==========================================
# TUE SEP 22: AEROBIC BASE CRUISE (7K)
# ==========================================
w_tue_run = {
    "workoutName": "W14D2: Zone 2 Aerobic Cruise [7K]",
    "description": "Steady aerobic base cruise. Lock into Zone 2 (162-172 bpm). Keep cadence light and snappy (~175+ spm).",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 2400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
            make_step(2, "interval", 3, _DIST(5500), "5.5 km Zone 2 Aerobic Cruise (162-172 bpm)", _hr_target(162, 172)),
            make_step(3, "cooldown", 2, _DIST(500), "500m Cooldown Walk/Jog", _hr_target(130, 150))
        ]
    }],
    "target_date": "2026-09-22"
}
workouts_to_schedule.append(w_tue_run)

# TUE SEP 22: UPPER BODY PUSH & CORE
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
    "workoutName": "W14D2: Upper Push & Core [AF Taft]",
    "description": "Upper body push hypertrophy and core stability. Chest, triceps, anterior shoulders, planks. STRICT VETO ON LEGS.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": push_steps
    }],
    "target_date": "2026-09-22"
}
workouts_to_schedule.append(w_tue_push)

# ==========================================
# WED SEP 23: THRESHOLD SPEED ANCHOR (5x1k)
# ==========================================
wed_steps = [
    make_step(1, "warmup", 1, _DIST(2000), "2.0 km Easy Warmup (<162 bpm)", _hr_target(130, 161))
]
cur_order = 2
for rep in range(5):
    # 1,000m Threshold
    wed_steps.append(make_step(cur_order, "interval", 3, _DIST(1000), f"Rep {rep+1}/5: 1,000m Threshold @ 4:15-4:25/km", _hr_target(181, 191)))
    cur_order += 1
    # 90s recovery jog
    wed_steps.append(make_step(cur_order, "recovery", 4, _TIME(90), f"Recovery {rep+1}/5: 90s Easy Jog (<155 bpm)", _hr_target(130, 155)))
    cur_order += 1

wed_steps.append(make_step(cur_order, "cooldown", 2, _DIST(1500), "1.5 km Cooldown Jog/Walk", _hr_target(130, 155)))

w_wed = {
    "workoutName": "W14D3: Quality Threshold Anchor [5x1k]",
    "description": "Speed endurance anchor: 2k warmup + 5x1,000m @ 4:15-4:25/km (Zone 4, 181-191 bpm) with 90s jog recovery + 1.5k cooldown. Elevate lactate threshold!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 3000,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": wed_steps
    }],
    "target_date": "2026-09-23"
}
workouts_to_schedule.append(w_wed)

# ==========================================
# THU SEP 24: CONDO POOL FLUSH & UPPER PULL
# ==========================================
w_thu_swim = {
    "workoutName": "W14D4: Condo Pool Flush [35m]",
    "description": "Hydrotherapy active recovery: 35m gentle swim/float flush in condo pool. Hydrostatic compression flushes micro-edema. Pure concentric, 0.0 ground reaction force.",
    "sportType": {"sportTypeId": 4, "sportTypeKey": "swimming"},
    "estimatedDurationInSecs": 2100,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 4, "sportTypeKey": "swimming"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _TIME(300), "5m Easy Freestyle/Breaststroke Warmup"),
            make_step(2, "interval", 3, _TIME(1500), "25m Relaxed Continuous Swim / Flutter Kicks"),
            make_step(3, "cooldown", 2, _TIME(300), "5m Water Treading / Deep Breathing Float")
        ]
    }],
    "target_date": "2026-09-24"
}
workouts_to_schedule.append(w_thu_swim)

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
    "workoutName": "W14D4: Upper Pull & Core [AF Taft]",
    "description": "Posterior chain pulling strength: Lat pulldowns, seated cable rows, face pulls, lateral raises, and core. ZERO LEGS to keep calves 100% fresh.",
    "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "estimatedDurationInSecs": 2400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
        "workoutSteps": pull_steps
    }],
    "target_date": "2026-09-24"
}
workouts_to_schedule.append(w_thu_pull)

# ==========================================
# FRI SEP 25: AEROBIC FOUNDATION + STRIDES (7.5K)
# ==========================================
fri_steps = [
    make_step(1, "warmup", 1, _DIST(1000), "1.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
    make_step(2, "interval", 3, _DIST(6000), "6.0 km Zone 2 Aerobic Cruise (162-172 bpm)", _hr_target(162, 172))
]
f_ord = 3
for rep in range(4):
    fri_steps.append(make_step(f_ord, "interval", 3, _DIST(100), f"Stride {rep+1}/4: 100m Fast Relaxed Acceleration (~3:45-3:55/km)"))
    f_ord += 1
    fri_steps.append(make_step(f_ord, "recovery", 4, _DIST(100), f"Recovery {rep+1}/4: 100m Easy Walk/Jog"))
    f_ord += 1

fri_steps.append(make_step(f_ord, "cooldown", 2, _DIST(200), "200m Cooldown Walk", _hr_target(130, 150)))

w_fri = {
    "workoutName": "W14D5: Aerobic Foundation + Strides [7.5K]",
    "description": "Smooth Zone 2 aerobic volume followed by 4x100m relaxed strides to open hip flexors and prime neuromuscular turnover.",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 2700,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": fri_steps
    }],
    "target_date": "2026-09-25"
}
workouts_to_schedule.append(w_fri)

# ==========================================
# SAT SEP 26: PRE-LONG RUN PRIMING SHAKEOUT (4K)
# ==========================================
w_sat = {
    "workoutName": "W14D6: Pre-Long Run Priming Shakeout [4K]",
    "description": "Short, effortless shakeout to keep neuromuscular turnover alive. Keep HR strictly Zone 1 (<148 bpm). Hydrate and carb-load today!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 1500,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "interval", 3, _DIST(4000), "4.0 km Easy Shakeout (<148 bpm)", _hr_target(130, 148))
        ]
    }],
    "target_date": "2026-09-26"
}
workouts_to_schedule.append(w_sat)

# ==========================================
# SUN SEP 27: BUILD II MILESTONE LONG RUN (24K)
# ==========================================
w_sun = {
    "workoutName": "W14D7: Build II Long Run [24K]",
    "description": "Milestone 24.0 km progressive aerobic long run. Steady Zone 2 (162-172 bpm). Mandatory marathon fueling practice: Take 3-4 energy gels with water at Km 7, 13, and 18!",
    "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
    "estimatedDurationInSecs": 8400,
    "workoutSegments": [{
        "segmentOrder": 1,
        "sportType": {"sportTypeId": 1, "sportTypeKey": "running"},
        "workoutSteps": [
            make_step(1, "warmup", 1, _DIST(2000), "2.0 km Easy Warmup (<160 bpm)", _hr_target(130, 160)),
            make_step(2, "interval", 3, _DIST(20000), "20.0 km Progressive Zone 2 (Gels at Km 7, 13, 18)", _hr_target(162, 172)),
            make_step(3, "cooldown", 2, _DIST(2000), "2.0 km Cooldown Walk/Jog", _hr_target(130, 150))
        ]
    }],
    "target_date": "2026-09-27"
}
workouts_to_schedule.append(w_sun)

# UPLOAD AND SCHEDULE EACH
print(f"Uploading and scheduling {len(workouts_to_schedule)} workouts for Week 14...")
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

