"""
core_tolerance_engine.py — Mechanical Load Tracker
=============================================
Calculates Mechanical ACWR (Acute:Chronic Workload Ratio) based on running distance.
Acts as a structural safeguard. If Mechanical ACWR > 1.3, flags WARNING. If > 1.5, flags OVERRIDE.
"""

from datetime import date, timedelta
from typing import Dict, Any

ACWR_WARNING_THRESHOLD = 1.3
ACWR_DANGER_THRESHOLD = 1.5

def calculate_mechanical_load(client) -> Dict[str, Any]:
    """
    Fetches running activities over the past 28 days to calculate Mechanical ACWR.
    Returns a dictionary with ACWR, acute load, chronic load, and safety flags.
    """
    today = date.today()
    start_chronic = today - timedelta(days=27)
    
    # Fetch activities for the last 28 days
    activities = client.get_activities_by_date(
        start_chronic.isoformat(), 
        today.isoformat(), 
        'running'
    )
    
    chronic_distance_km = 0.0
    acute_distance_km = 0.0
    
    acute_start = today - timedelta(days=6)
    
    for act in activities:
        act_date_str = act.get('startTimeLocal', '')[:10]
        if not act_date_str:
            continue
            
        act_date = date.fromisoformat(act_date_str)
        dist_km = act.get('distance', 0) / 1000.0
        
        chronic_distance_km += dist_km
        if act_date >= acute_start:
            acute_distance_km += dist_km

    # Averages
    acute_avg = acute_distance_km / 7.0
    chronic_avg = chronic_distance_km / 28.0
    
    if chronic_avg == 0:
        acwr = 1.0 # default if no history
    else:
        acwr = acute_avg / chronic_avg

    requires_deload = acwr > ACWR_DANGER_THRESHOLD
    warning = acwr > ACWR_WARNING_THRESHOLD

    return {
        "mechanical_acwr": round(acwr, 3),
        "acute_distance_km": round(acute_distance_km, 2),
        "chronic_distance_km": round(chronic_distance_km, 2),
        "acute_avg_km_day": round(acute_avg, 2),
        "chronic_avg_km_day": round(chronic_avg, 2),
        "warning": warning,
        "requires_deload": requires_deload
    }

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from garminconnect import Garmin

    load_dotenv(r'c:\Users\Max\OneDrive - De La Salle University - Manila\marathon-agent\.env')
    client = Garmin(os.getenv('GARMIN_EMAIL'), os.getenv('GARMIN_PASSWORD'))
    client.login(os.path.expanduser('~/.garminconnect'))
    
    res = calculate_mechanical_load(client)
    print("--- Running Tolerance (Mechanical ACWR) ---")
    print(f"Acute (7d) Total : {res['acute_distance_km']} km")
    print(f"Chronic (28d) Total : {res['chronic_distance_km']} km")
    print(f"Mechanical ACWR: {res['mechanical_acwr']}")
    print(f"Warning: {res['warning']} | Deload Required: {res['requires_deload']}")
