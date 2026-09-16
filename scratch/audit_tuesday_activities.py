import os
from datetime import date
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(
    email=os.getenv("GARMIN_EMAIL"),
    password=os.getenv("GARMIN_PASSWORD"),
    prompt_mfa=lambda: input("MFA: "),
)
client.login(TOKEN_STORE)

today = date.today()
print(f"=== DEEP AUDIT: ACTIVITIES FOR {today} ===")

acts = client.get_activities_by_date(today.isoformat(), today.isoformat())
print(f"Total activities today: {len(acts)}")

for a in acts:
    act_id = a.get("activityId")
    name = a.get("activityName")
    t = a.get("activityType", {}).get("typeKey")
    start = a.get("startTimeLocal")
    dist = (a.get("distance") or 0) / 1000
    dur = (a.get("duration") or 0) / 60
    mov_dur = (a.get("movingDuration") or 0) / 60
    ahr = a.get("averageHR")
    mhr = a.get("maxHR")
    ae = a.get("aerobicTrainingEffect")
    an = a.get("anaerobicTrainingEffect")
    elev = a.get("elevationGain")
    cal = a.get("calories")
    speed = a.get("averageSpeed")
    p_str = "-"
    if speed and speed > 0:
        if "running" in t:
            s = 1000 / speed
            p_str = f"{int(s//60)}:{int(s%60):02d}/km"
        elif "cycling" in t:
            p_str = f"{speed*3.6:.1f} km/h"
    
    print(f"\n=======================================================")
    print(f"[{start}] ID: {act_id} | {t.upper()} | {name}")
    print(f"=======================================================")
    print(f"  Distance:     {dist:.2f} km | Elapsed: {dur:.1f} min | Moving: {mov_dur:.1f} min | Pace: {p_str}")
    print(f"  Heart Rate:   {ahr} avg / {mhr} max bpm")
    print(f"  Training Eff: Aerobic {ae} | Anaerobic {an}")
    print(f"  Elev / Cal:   +{elev} m | {cal} kcal")

    if "running" in t:
        splits = client.get_activity_splits(act_id)
        if splits and "lapDTOs" in splits:
            print("  --- LAP BREAKDOWN ---")
            for idx, lap in enumerate(splits["lapDTOs"]):
                ldist = (lap.get("distance") or 0) / 1000
                lmov = (lap.get("movingDuration") or 0) / 60
                lhr = lap.get("averageHR")
                lmhr = lap.get("maxHR")
                lspeed = lap.get("averageSpeed")
                lp_str = "-"
                if lspeed and lspeed > 0:
                    ls = 1000 / lspeed
                    lp_str = f"{int(ls//60)}:{int(ls%60):02d}/km"
                lcad = lap.get("averageRunningCadenceInStepsPerMinute")
                lstride = (lap.get("strideLength") or 0) / 100
                lgct = lap.get("groundContactTime")
                lvo = lap.get("verticalOscillation")
                lpow = lap.get("averagePower")
                lelev = lap.get("elevationGain") or 0
                print(f"    Lap {idx+1:2d}: {ldist:4.2f}km | {lmov:4.2f}m ({lp_str}) | HR: {str(lhr):>3}/{str(lmhr):<3} bpm | Cad: {str(lcad):>3}spm | Stride: {lstride:.2f}m | GCT: {str(lgct)[:3]}ms | Pow: {lpow}W | +{lelev}m")

# Daily vitals
summary = client.get_user_summary(today.isoformat())
print("\n--- DAILY TOTALS ---")
print(f"  Steps:           {summary.get('totalSteps')}")
print(f"  Total Distance:  {(summary.get('totalDistanceMeters') or 0)/1000:.2f} km")
print(f"  Active Calories: {summary.get('activeKilocalories')} kcal | Total: {summary.get('totalKilocalories')} kcal")
print(f"  Body Battery:    {summary.get('bodyBatteryMostRecentValue')} (High: {summary.get('bodyBatteryHighestValue')}, Low: {summary.get('bodyBatteryLowestValue')})")
print(f"  Stress Avg:      {summary.get('averageStressLevel')} / 100")
