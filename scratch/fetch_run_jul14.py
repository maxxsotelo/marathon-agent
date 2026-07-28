import os, sys
sys.path.insert(0, r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent")
from dotenv import load_dotenv
load_dotenv(r"c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env")
from garminconnect import Garmin

TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

acts = client.get_activities_by_date("2026-07-14", "2026-07-14")
print(f"Activities on 2026-07-14: {len(acts)} found\n")
for a in acts:
    sport = a.get("activityType", {}).get("typeKey", "unknown")
    name = a.get("activityName", "N/A")
    act_id = a.get("activityId")
    dur = (a.get("duration", 0) or 0) / 60
    dist = (a.get("distance", 0) or 0) / 1000
    avg_hr = a.get("averageHR", 0) or 0
    max_hr = a.get("maxHR", 0) or 0
    aer_te = a.get("aerobicTrainingEffect", 0) or 0
    kcal = a.get("calories", 0) or 0
    avg_cad = a.get("averageRunningCadenceInStepsPerMinute", 0) or 0
    avg_pace_ms = a.get("averageSpeed", 0) or 0
    print(f"[{sport.upper()}] {name} (ID: {act_id})")
    print(f"  Distance: {dist:.2f} km | Duration: {dur:.1f} min")
    print(f"  Avg HR: {avg_hr:.0f} bpm | Max HR: {max_hr:.0f} bpm")
    print(f"  Aer TE: {aer_te:.1f} | Calories: {kcal:.0f} kcal | Avg Cadence: {avg_cad:.0f} spm")
    print()
    if "running" in sport:
        try:
            splits = client.get_activity_splits(str(act_id))
            laps = splits.get("lapDTOs", [])
            print(f"  Lap  Dist(m)   Pace      AvgHR   MaxHR   Cad")
            print(f"  " + "-"*55)
            for i, lap in enumerate(laps, 1):
                lap_dist = lap.get("distance", 0) or 0
                lap_dur = lap.get("duration", 0) or 0
                lap_hr = lap.get("averageHR", 0) or 0
                lap_max_hr = lap.get("maxHR", 0) or 0
                lap_cad = lap.get("averageRunCadence", 0) or 0
                if lap_dist > 0 and lap_dur > 0:
                    pace_sec = (lap_dur / lap_dist) * 1000
                    pace_min = int(pace_sec // 60)
                    pace_s = int(pace_sec % 60)
                    pace_str = f"{pace_min}:{pace_s:02d}"
                else:
                    pace_str = "--:--"
                print(f"  {i:<4} {lap_dist:<9.0f} {pace_str:<9} {lap_hr:<7.0f} {lap_max_hr:<7.0f} {lap_cad:.0f}")
            print()
        except Exception as e:
            print(f"  Lap data error: {e}")
