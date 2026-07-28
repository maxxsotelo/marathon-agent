"""
fetch_vo2max_and_te.py
Pulls VO2 Max progression + Training Effect from Garmin Connect
"""
import os, sys
from datetime import date, timedelta
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 26)

# ---- 1. VO2 MAX HISTORY ----
print("=== VO2 MAX PROGRESSION (Garmin Endpoint) ===")
try:
    vo2_data = client.get_vo2max_summary_data(today.isoformat())
    if vo2_data:
        for entry in vo2_data:
            print(entry)
    else:
        print("No data returned from vo2max_summary endpoint")
except Exception as e:
    print(f"vo2max_summary error: {e}")

print()

# ---- 2. TRAINING STATUS (includes VO2 Max + Load Balance) ----
print("=== TRAINING STATUS ===")
try:
    ts = client.get_training_status(today.isoformat())
    if ts:
        print(f"VO2 Max:           {ts.get('mostRecentVO2Max')}")
        print(f"Training Status:   {ts.get('mostRecentTrainingStatus')}")
        print(f"Load Balance:      {ts.get('mostRecentTrainingLoadBalance')}")
        print(f"Full response keys: {list(ts.keys())}")
        # Print everything
        for k, v in ts.items():
            if v is not None:
                print(f"  {k}: {v}")
    else:
        print("No training status data")
except Exception as e:
    print(f"Training status error: {e}")

print()

# ---- 3. FITNESS AGE ----
print("=== FITNESS AGE ===")
try:
    fitness_age = client.get_fitnessage_data(today.isoformat())
    if fitness_age:
        for k, v in fitness_age.items():
            if v is not None:
                print(f"  {k}: {v}")
except Exception as e:
    print(f"Fitness age error: {e}")

print()

# ---- 4. TRAINING EFFECT PER SESSION (last 14 days) ----
print("=== TRAINING EFFECT — LAST 14 DAYS (Running only) ===")
start = (today - timedelta(days=14)).isoformat()
acts = client.get_activities_by_date(start, today.isoformat())

seen_ids = set()
for a in acts:
    act_id = a.get("activityId")
    if act_id in seen_ids:
        continue
    seen_ids.add(act_id)

    sport = a.get("activityType", {}).get("typeKey", "")
    if sport not in ("running", "treadmill_running", "hiit", "indoor_cardio"):
        continue

    name = a.get("activityName", "?")
    d = a.get("startTimeLocal", "?")[:10]
    dist = (a.get("distance") or 0) / 1000
    avg_hr = a.get("averageHR", "-")
    max_hr = a.get("maxHR", "-")
    ae = a.get("aerobicTrainingEffect", None)
    an = a.get("anaerobicTrainingEffect", None)
    label = a.get("trainingEffectLabel", "-")
    benefit = a.get("trainingEffectLabel", "-")
    ae_msg = a.get("aerobicTrainingEffectMessage", "-")
    an_msg = a.get("anaerobicTrainingEffectMessage", "-")
    recovery_hrs = a.get("recoveryTime", None)

    ae_str = f"{float(ae):.1f}" if ae is not None else "-"
    an_str = f"{float(an):.1f}" if an is not None else "-"

    print(f"{d} | [{sport.upper()}] {name}")
    print(f"  Dist: {dist:.2f}km | HR: {avg_hr}/{max_hr}")
    print(f"  Aerobic TE:    {ae_str}/5.0 — {ae_msg}")
    print(f"  Anaerobic TE:  {an_str}/5.0")
    print(f"  Benefit Label: {benefit}")
    print(f"  Recovery Time: {recovery_hrs} hrs")
    print()

# ---- 5. VO2 MAX RACE PREDICTIONS ----
print("=== RACE TIME PREDICTIONS (from Garmin) ===")
try:
    # Try the race predictions endpoint
    race_preds = client.get_race_predictions()
    if race_preds:
        for k, v in race_preds.items():
            if v is not None:
                print(f"  {k}: {v}")
    else:
        print("No race prediction data returned")
except Exception as e:
    print(f"Race predictions error: {e}")

print()
print("=== VO2 MAX RAW VIA TRAINING STATUS DETAIL ===")
try:
    # Try alternate endpoint
    detail = client.get_training_readiness(today.isoformat())
    if detail:
        for k, v in detail.items():
            if v is not None:
                print(f"  {k}: {v}")
except Exception as e:
    print(f"Training readiness error: {e}")
