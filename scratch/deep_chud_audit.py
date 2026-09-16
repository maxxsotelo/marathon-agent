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

# Activity ID for today's run
act_id = "24008892657"

# Pull activity details
act = client.get_activity(act_id)
splits = client.get_activity_splits(act_id)
details = client.get_activity_details(act_id)
hr_zones = client.get_activity_hr_in_timezones(act_id)

print("=== DEEP RUN AUDIT: CHUD RUN (2026-08-17) ===")
summary = act.get("summaryDTO", {})
print(f"Name:         {act.get('activityName')}")
print(f"Distance:     {summary.get('distance', 0)/1000:.2f} km")
print(f"Duration:     {summary.get('duration', 0)/60:.1f} min ({summary.get('movingDuration', 0)/60:.1f} min moving)")
print(f"Pace:         {1000/summary.get('averageSpeed', 1)/60:.2f} min/km (Avg Speed: {summary.get('averageSpeed')*3.6:.2f} km/h)")
print(f"Max Speed:    {1000/summary.get('maxSpeed', 1)/60:.2f} min/km ({summary.get('maxSpeed')*3.6:.2f} km/h)")
print(f"Heart Rate:   {summary.get('averageHR')} avg / {summary.get('maxHR')} max bpm")
print(f"Cadence:      {summary.get('averageRunningCadenceInStepsPerMinute')} avg / {summary.get('maxRunningCadenceInStepsPerMinute')} max spm")
print(f"Stride:       {summary.get('strideLength', 0)/100:.2f} m")
print(f"GCT:          {summary.get('groundContactTime')} ms")
print(f"Vert Osc:     {summary.get('verticalOscillation')} cm | Ratio: {summary.get('verticalRatio')} %")
print(f"Avg Power:    {summary.get('avgPower')} W | Max Power: {summary.get('maxPower')} W")
print(f"Elevation:    +{summary.get('elevationGain')} m / -{summary.get('elevationLoss')} m")
print(f"Calories:     {summary.get('calories')} kcal")
print(f"Training Eff: Aerobic {summary.get('trainingEffect')} | Anaerobic {summary.get('anaerobicTrainingEffect')}")
print(f"Temp:         Avg {summary.get('avgTemperature')} C | Max {summary.get('maxTemperature')} C")

print("\n--- LAP BREAKDOWN ---")
if splits and "lapDTOs" in splits:
    for i, lap in enumerate(splits["lapDTOs"]):
        dist = (lap.get("distance") or 0) / 1000
        dur = (lap.get("duration") or 0) / 60
        mov = (lap.get("movingDuration") or 0) / 60
        speed = lap.get("averageSpeed") or 0
        pace = f"{int(1000/speed//60)}:{int(1000/speed%60):02d}/km" if speed > 0 else "-"
        ahr = lap.get("averageHR")
        mhr = lap.get("maxHR")
        cad = lap.get("averageRunningCadenceInStepsPerMinute")
        stride = (lap.get("strideLength") or 0) / 100
        gct = lap.get("groundContactTime")
        vo = lap.get("verticalOscillation")
        pwr = lap.get("averagePower")
        elev = lap.get("elevationGain") or 0
        print(f"  Lap {i+1:2d}: {dist:4.2f}km | {mov:4.2f}m ({pace}) | HR: {str(ahr):>3}/{str(mhr):<3} bpm | Cad: {cad} spm | Stride: {stride:.2f}m | GCT: {gct}ms | Pow: {pwr}W | Elev: +{elev}m")

print("\n--- HR ZONE DISTRIBUTION ---")
if hr_zones:
    print(f"HR Zones data: {hr_zones}")
