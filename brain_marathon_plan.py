"""
brain_marathon_plan.py - Antigravity Marathon Training Master Plan
SOURCE OF TRUTH for all marathon training block decisions.
AGENTS MUST CHECK THIS FILE (Rule 02) before prescribing weekly sessions.
Run: python brain_marathon_plan.py  to see current block status.

Race:      Capas / New Clark City Marathon (TBD - waiting for official announcement)
Planning:  ~Nov 30, 2026 (adjust once confirmed)
Athlete:   Max | Goal weight: 70.0 kg | Current: 74.4 kg
Generated: 2026-06-18
"""
import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from datetime import date, timedelta


RACE_NAME     = "Capas / New Clark City Full Marathon"
RACE_DATE_TBD = True
RACE_DATE     = date(2026, 11, 30)
RACE_DISTANCE = 42.195

ATHLETE = {
    "name": "Max",
    "current_weight": 74.4,
    "goal_weight":    70.0,
    "current_vo2max": 52.0,
    "lthr": 191,
    "rhr":  39,
    "max_hr": 206,
}

HR_ZONES = {
    "Z1": {"name": "Easy Aerobic", "low": 130, "high": 161},
    "Z2": {"name": "Extensive",    "low": 162, "high": 174},
    "Z3": {"name": "Tempo",        "low": 174, "high": 181},
    "Z4": {"name": "Threshold",    "low": 181, "high": 191},
    "Z5": {"name": "VO2 Max",      "low": 191, "high": 206},
}

TREADMILL_RULES = {
    "motorized_incline":      1.5,
    "max_treadmill_long_run": 22,
    "notes": "Manual/curved preferred. Motorized MUST use 1.5-2% incline. LR > 22km = outdoor only.",
}

BLOCKS = [
    {"name":"Base Rebuild",   "phase":1,"start":date(2026,6,22),"end":date(2026,8,3),
     "weeks":6,"weekly_km":(42,52),"long_run_km":(17,22),"calorie_deficit":-450,
     "weight_target":71.4,
     "notes":"Weight loss phase. 0.5 kg/wk deficit. High protein 2.2g/kg (~164g/day). Treadmill OK weekdays."},
    {"name":"Build I",        "phase":2,"start":date(2026,8,4),"end":date(2026,9,14),
     "weeks":6,"weekly_km":(52,60),"long_run_km":(22,28),"calorie_deficit":-175,
     "weight_target":70.5,
     "notes":"Volume ramps. Shrink deficit. 1x marathon-pace session/week (5:30-5:50/km)."},
    {"name":"Build II / Peak","phase":3,"start":date(2026,9,15),"end":date(2026,10,26),
     "weeks":6,"weekly_km":(58,65),"long_run_km":(28,35),"calorie_deficit":0,
     "weight_target":70.0,
     "notes":"No deficit. Eat to perform. Two 30+ km long runs. UPD 21K race simulation for pace calibration."},
    {"name":"Race Specific",  "phase":4,"start":date(2026,10,27),"end":date(2026,11,9),
     "weeks":2,"weekly_km":(50,56),"long_run_km":(25,30),"calorie_deficit":0,
     "weight_target":70.0,
     "notes":"Sharpen. Lock in race pace. Keep intensity honest."},
    {"name":"Taper",          "phase":5,"start":date(2026,11,10),"end":date(2026,11,29),
     "weeks":3,"weekly_km":(15,40),"long_run_km":(10,20),"calorie_deficit":0,
     "weight_target":70.0,
     "notes":"Volume -30-40% each week. Carb ramp +60-80g/day final 3 days. Trust the training."},
]

LONG_RUN_PROGRESSION = [
    (1, date(2026,6,21),  17, "First step-up. Zone 1."),
    (2, date(2026,6,28),  18, ""),
    (3, date(2026,7,5),   20, "First 20+ km of cycle"),
    (4, date(2026,7,12),  18, "CUTBACK"),
    (5, date(2026,7,19),  21, "Half-marathon distance"),
    (6, date(2026,7,26),  23, ""),
    (7, date(2026,8,2),   21, "CUTBACK"),
    (8, date(2026,8,9),   24, ""),
    (9, date(2026,8,16),  22, "CUTBACK"),
    (10,date(2026,8,23),  26, ""),
    (11,date(2026,8,30),  24, "CUTBACK"),
    (12,date(2026,9,6),   28, ""),
    (13,date(2026,9,13),  25, "CUTBACK"),
    (14,date(2026,9,20),  21, "UPD 21K RACE SIMULATION - marathon effort, hilly, calibrate goal pace"),
    (15,date(2026,9,27),  30, "First 30K of cycle"),
    (16,date(2026,10,4),  27, "CUTBACK"),
    (17,date(2026,10,11), 32, "PEAK LONG RUN #1"),
    (18,date(2026,10,18), 28, "CUTBACK"),
    (19,date(2026,10,25), 35, "PEAK LONG RUN #2 - longest run of cycle"),
    (20,date(2026,11,1),  28, ""),
    (21,date(2026,11,8),  25, ""),
    (22,date(2026,11,15), 20, "TAPER BEGINS"),
    (23,date(2026,11,22), 14, ""),
    (24,date(2026,11,29), 10, "Race-eve shakeout only"),
]

WEIGHT_TARGETS = [
    (date(2026,6,22), 74.4, "Current"),
    (date(2026,7,6),  73.6, "Wk 3"),
    (date(2026,7,20), 72.8, "Wk 5"),
    (date(2026,8,3),  71.9, "End Base Rebuild"),
    (date(2026,9,1),  70.8, "Wk 11"),
    (date(2026,9,15), 70.3, "End Build I"),
    (date(2026,10,1), 70.0, "GOAL WEIGHT - maintain"),
]

FLEXIBILITY_PROTOCOL = """
WORKING PROFESSIONAL PROTOCOL (BSP schedule):
- Missed weekday run: accept it, do NOT double up next day.
- Missed Sunday long run: reschedule to Saturday - this is the ONLY non-negotiable session.
- Short outdoor runs 5-10 km preferred over treadmill when time permits on weekdays.
- As pace improves, same km = less time. Plan naturally self-compresses.
- 2 missed weekday sessions/week: acceptable. 3+: flag for re-evaluation.
- Full week missed (illness/travel): return at 70% volume, not full load.
- Race date TBD: when Capas announces, update RACE_DATE and RACE_DATE_TBD=False.
"""

def get_current_block(today=None):
    today = today or date.today()
    for b in BLOCKS:
        if b["start"] <= today <= b["end"]:
            return b
    if today < BLOCKS[0]["start"]:
        return {"name":"Pre-Block (Base Rebuild starts Jun 22)","phase":0,
                "weekly_km":(40,45),"long_run_km":(15,17),"calorie_deficit":-450,"notes":""}
    return {"name":"Post-Plan / Race Week","phase":6,
            "weekly_km":(10,15),"long_run_km":(8,10),"calorie_deficit":0,"notes":""}

def get_long_run_target(today=None):
    today = today or date.today()
    days_to_sun = (6 - today.weekday()) % 7
    next_sun = today + timedelta(days=days_to_sun)
    for w,s,k,n in LONG_RUN_PROGRESSION:
        if s == next_sun:
            return w,s,k,n
    past = [(w,s,k,n) for w,s,k,n in LONG_RUN_PROGRESSION if s <= next_sun]
    if past: return past[-1]
    return None, next_sun, 17, "Default"

def weeks_to_race(today=None):
    today = today or date.today()
    return (RACE_DATE - today).days // 7

if __name__ == "__main__":
    today = date.today()
    block = get_current_block(today)
    lr_week,lr_date,lr_km,lr_notes = get_long_run_target(today)
    print("=" * 65)
    print("  ANTIGRAVITY MARATHON PLAN")
    print(f"  {RACE_NAME}")
    tbd_str = "(PLANNING DATE - NOT YET CONFIRMED)" if RACE_DATE_TBD else "(CONFIRMED)"
    print(f"  Race Date:     {RACE_DATE}  {tbd_str}")
    print(f"  Weeks to Race: {weeks_to_race(today)}")
    print("=" * 65)
    print(f"\n  ATHLETE  ({today})")
    print(f"  Weight:    {ATHLETE['current_weight']} kg  ->  Goal: {ATHLETE['goal_weight']} kg  (need -{round(ATHLETE['current_weight']-ATHLETE['goal_weight'],1)} kg)")
    print(f"  VO2 Max:   {ATHLETE['current_vo2max']}")
    print(f"\n  BLOCK:     {block['name']}  (Phase {block['phase']})")
    print(f"  Weekly km: {block['weekly_km'][0]}-{block['weekly_km'][1]} km")
    print(f"  Long run:  {block['long_run_km'][0]}-{block['long_run_km'][1]} km")
    print(f"  Cal def:   {block['calorie_deficit']} kcal/day")
    if block.get("notes"): print(f"  Notes:     {block['notes']}")
    print(f"\n  NEXT LONG RUN  Sunday {lr_date}")
    print(f"  Target: {lr_km} km")
    if lr_notes: print(f"  Notes:  {lr_notes}")
    print(f"\n  TREADMILL: always {TREADMILL_RULES['motorized_incline']}% incline | max indoor LR = {TREADMILL_RULES['max_treadmill_long_run']} km")
    print("\n" + "=" * 65)

