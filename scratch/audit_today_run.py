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
acts = client.get_activities_by_date(today.isoformat(), today.isoformat())

print(f"Activities today ({len(acts)}):")
for a in acts:
    act_id = a.get("activityId")
    name = a.get("activityName")
    t = a.get("activityType", {}).get("typeKey")
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
        s = 1000 / speed
        p_str = f"{int(s//60)}:{int(s%60):02d}/km"
    
    print(f"\nActivity ID: {act_id}")
    print(f"Name:        {name}")
    print(f"Type:        {t}")
    print(f"Distance:    {dist:.2f} km")
    print(f"Elapsed Time:{dur:.1f} min ({int(dur//60)}h {int(dur%60)}m)")
    print(f"Moving Time: {mov_dur:.1f} min ({int(mov_dur//60)}h {int(mov_dur%60)}m)")
    print(f"Avg Pace:    {p_str}")
    print(f"Avg / Max HR:{ahr} / {mhr} bpm")
    print(f"Training Eff:Aerobic {ae} | Anaerobic {an}")
    print(f"Elevation:   +{elev} m")
    print(f"Calories:    {cal} kcal")
    
    # Laps
    print("\n--- LAPS ---")
    splits = client.get_activity_splits(act_id)
    if splits and "lapDTOs" in splits:
        for idx, lap in enumerate(splits["lapDTOs"]):
            ldist = (lap.get("distance") or 0) / 1000
            ldur = (lap.get("duration") or 0) / 60
            lmov = (lap.get("movingDuration") or 0) / 60
            lhr = lap.get("averageHR")
            lmhr = lap.get("maxHR")
            lspeed = lap.get("averageSpeed")
            lp_str = "-"
            if lspeed and lspeed > 0:
                ls = 1000 / lspeed
                lp_str = f"{int(ls//60)}:{int(ls%60):02d}/km"
            lcad = lap.get("averageRunningCadenceInStepsPerMinute")
            lpow = lap.get("averagePower")
            print(f"  Lap {idx+1:2d}: {ldist:4.2f} km | Mov: {lmov:4.2f}m ({lp_str}) | HR: {str(lhr):>3}/{str(lmhr):<3} bpm | Cad: {lcad} spm | Pow: {lpow}W")
