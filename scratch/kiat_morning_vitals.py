"""
kiat_morning_vitals.py
Uses Garmin data to generate a Kiat Engine morning diagnostic.
"""
import os, sys
from datetime import date
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin
from core_physiological_engine import PhysiologicalEngine

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date(2026, 7, 28).isoformat()
print(f"=== KIAT ENGINE — MORNING DIAGNOSTICS FOR {today} ===")

# Fetch Garmin Vitals
bb, rhr, stress = 'N/A', 'N/A', 'N/A'
try:
    summary = client.get_user_summary(today)
    bb = summary.get('bodyBatteryMostRecentValue', 'N/A')
    rhr = summary.get('restingHeartRate', 'N/A')
    stress = summary.get('averageStressLevel', 'N/A')
except: pass

hrv_status, hrv_last, hrv_weekly = 'N/A', 'N/A', 'N/A'
try:
    hrv = client.get_hrv_data(today)
    if hrv:
        hrv_status = hrv.get('hrvSummary', {}).get('status', 'N/A')
        hrv_last = hrv.get('hrvSummary', {}).get('lastNightAvg', 'N/A')
        hrv_weekly = hrv.get('hrvSummary', {}).get('weeklyAvg', 'N/A')
except: pass

sleep_score, sleep_time = 'N/A', 'N/A'
try:
    sleep = client.get_sleep_data(today)
    if sleep:
        sleep_score = sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value', 'N/A')
        secs = sleep.get('dailySleepDTO', {}).get('sleepTimeSeconds', None)
        if secs:
            sleep_time = f"{secs // 3600}h {(secs % 3600) // 60}m"
except: pass

readiness_score, recovery_time = 'N/A', 'N/A'
try:
    readiness = client.get_training_readiness(today)
    if readiness:
        readiness_score = readiness.get('readinessScore', 'N/A')
        recovery_time = readiness.get('recoveryTime', 'N/A')
except: pass

print(f"Body Battery:       {bb}/100")
print(f"Resting HR:         {rhr} bpm")
print(f"Stress Score:       {stress}")
print(f"HRV Last Night:     {hrv_last} ms")
print(f"HRV Weekly Avg:     {hrv_weekly} ms ({hrv_status})")
print(f"Sleep Score:        {sleep_score} ({sleep_time})")
print(f"Garmin Readiness:   {readiness_score}/100")
print(f"Recovery Hours Left:{recovery_time}h")

# Use Kiat Engine to compute TRS
engine = PhysiologicalEngine()

try:
    hrs_sleep = 0
    if isinstance(secs, (int, float)):
        hrs_sleep = secs / 3600.0

    trs = engine.compute_readiness_score(
        sleep_score=float(sleep_score) if sleep_score != 'N/A' else 75.0,
        sleep_hours=hrs_sleep if hrs_sleep > 0 else 7.5,
        hrv_last_night=float(hrv_last) if hrv_last != 'N/A' else 116.0,
        hrv_baseline=float(hrv_weekly) if hrv_weekly != 'N/A' else 116.0,
        rhr=float(rhr) if rhr != 'N/A' else 40.0,
        rhr_baseline=40.0,
        stress_score=float(stress) if stress != 'N/A' else 25.0
    )
    print(f"\nKIAT ENGINE TRS:    {trs:.1f}/100")
    if trs >= 90:
        print("STATUS: PRIME (Cleared for Max Effort)")
    elif trs >= 75:
        print("STATUS: PRIMED (Cleared for Quality/Volume)")
    elif trs >= 50:
        print("STATUS: MODERATE (Cap HR at Zone 2)")
    else:
        print("STATUS: LOW (Rest / Zone 1 Only)")
except Exception as e:
    print(f"\nKiat Engine computation error: {e}")
