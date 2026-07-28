import os
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
TOKEN_STORE = os.path.expanduser("~/.garminconnect")
client = Garmin(email=os.getenv("GARMIN_EMAIL"), password=os.getenv("GARMIN_PASSWORD"))
client.login(TOKEN_STORE)

details = client.get_activity(23440767740)
s = details.get("summaryDTO", {})

print("=== TEMPO RUN — Full Summary ===")
dist = round((s.get("distance") or 0) / 1000, 2)
dur = round((s.get("duration") or 0) / 60, 1)
spd = s.get("averageSpeed", None)
pace_str = "N/A"
if spd and spd > 0:
    p = 1000 / spd / 60
    pace_str = f"{int(p)}:{int((p - int(p))*60):02d} /km"

print(f"  Distance:           {dist} km")
print(f"  Duration:           {dur} min")
print(f"  Avg Pace:           {pace_str}")
print(f"  Avg HR:             {s.get('averageHR')} bpm")
print(f"  Max HR:             {s.get('maxHR')} bpm")
print(f"  Avg Cadence:        {s.get('averageRunCadence')} spm")
print(f"  Aerobic TE:         {s.get('trainingEffect')}")
print(f"  Anaerobic TE:       {s.get('anaerobicTrainingEffect')}")
print(f"  TE Label:           {s.get('trainingEffectLabel')}")
print(f"  Aerobic TE Msg:     {s.get('aerobicTrainingEffectMessage')}")
print(f"  Anaerobic TE Msg:   {s.get('anaerobicTrainingEffectMessage')}")
print(f"  Calories:           {s.get('calories')}")
print(f"  Avg Temp:           {s.get('averageTemperature')} C")
print(f"  Max Temp:           {s.get('maxTemperature')} C")
print(f"  Vertical Osc:       {s.get('verticalOscillation')} mm")
print(f"  Ground Contact:     {s.get('groundContactTime')} ms")
print(f"  Stride Length:      {s.get('strideLength')} m")
print(f"  Vert Ratio:         {s.get('verticalRatio')} %")
print(f"  Body Battery Delta: {s.get('differenceBodyBattery')}")
print(f"  RPE:                {s.get('directWorkoutRpe')}")

# Splits
splits = details.get("splitSummaries", [])
print(f"\n=== Split Summaries ({len(splits)}) ===")
for sp in splits:
    nm = sp.get("noOfSplits", "?")
    ty = sp.get("splitType", "?")
    tot = round((sp.get("distance") or 0) / 1000, 2)
    print(f"  {ty}: {nm} splits, {tot} km total")
