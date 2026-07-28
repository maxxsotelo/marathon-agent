import os
import json
from datetime import date, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()

activities = client.get_activities_by_date(yesterday, today)

print(f"=== Activities on {today} ===")
for act in activities:
    act_date = act.get("startTimeLocal", "")[:10]
    if act_date == today:
        act_id = act.get("activityId")
        name   = act.get("activityName", "N/A")
        dist   = round((act.get("distance") or 0) / 1000, 2)
        dur    = round((act.get("duration") or 0) / 60, 1)
        hr_avg = act.get("averageHR", "N/A")
        hr_max = act.get("maxHR", "N/A")
        te_aer = act.get("aerobicTrainingEffect", "N/A")
        te_ana = act.get("anaerobicTrainingEffect", "N/A")
        epoc   = act.get("anaerobicTrainingEffect", "N/A")
        hrv    = act.get("hrv", "N/A")
        sport  = act.get("activityType", {}).get("typeKey", "N/A")
        avg_run_cadence = act.get("averageRunningCadenceInStepsPerMinute", "N/A")
        avg_pace = act.get("averageSpeed", None)
        if avg_pace and avg_pace > 0:
            pace_min = 1000 / avg_pace / 60
            pace_str = f"{int(pace_min)}:{int((pace_min - int(pace_min)) * 60):02d} /km"
        else:
            pace_str = "N/A"
        print(f"\n--- {name} ---")
        print(f"  ID:         {act_id}")
        print(f"  Sport:      {sport}")
        print(f"  Distance:   {dist} km")
        print(f"  Duration:   {dur} min")
        print(f"  Avg Pace:   {pace_str}")
        print(f"  Avg HR:     {hr_avg} bpm")
        print(f"  Max HR:     {hr_max} bpm")
        print(f"  Cadence:    {avg_run_cadence} spm")
        print(f"  Aer TE:     {te_aer}")
        print(f"  Ana TE:     {te_ana}")

        # Fetch laps
        try:
            details = client.get_activity(act_id)
            laps = details.get("splits", {}).get("lapDTOs", [])
            if laps:
                print(f"\n  Laps ({len(laps)}):")
                for i, lap in enumerate(laps):
                    lkm = round((lap.get("distance") or 0) / 1000, 2)
                    lhr = lap.get("averageHR", "N/A")
                    lmax = lap.get("maxHR", "N/A")
                    lspd = lap.get("averageSpeed", None)
                    if lspd and lspd > 0:
                        lp = 1000 / lspd / 60
                        lpace = f"{int(lp)}:{int((lp - int(lp)) * 60):02d}"
                    else:
                        lpace = "N/A"
                    print(f"    Lap {i+1:2d}: {lkm:5.2f} km | {lpace} /km | Avg HR: {lhr} | Max HR: {lmax}")
        except Exception as e:
            print(f"  Laps error: {e}")
