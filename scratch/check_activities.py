import os
import json
from datetime import date, timedelta
from garminconnect import Garmin

def get_garmin_client():
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    if not email or not password:
        from dotenv import load_dotenv
        load_dotenv()
        email = os.environ.get("GARMIN_EMAIL")
        password = os.environ.get("GARMIN_PASSWORD")
    
    tokenstore = os.path.expanduser("~/.garminconnect")
    try:
        with open(tokenstore, "r") as f:
            tokens = json.load(f)
            client = Garmin()
            client.login(tokenstore)
            return client
    except Exception as e:
        client = Garmin(email, password)
        client.login()
        with open(tokenstore, "w") as f:
            json.dump(client.garth.oauth2_token, f)
        return client

def main():
    try:
        client = get_garmin_client()
        today = date.today()
        start_date = today - timedelta(days=28)
        activities = client.get_activities_by_date(start_date.isoformat(), today.isoformat())
        
        acute_km = 0.0
        chronic_km = 0.0
        
        print("--- LAST 10 DAYS RUNNING ACTIVITIES ---")
        run_types = ("running", "treadmill_running", "trail_running", "indoor_running")
        for a in sorted(activities, key=lambda x: x.get('startTimeLocal', '')):
            atype = a.get("activityType", {}).get("typeKey")
            if atype not in run_types:
                continue
                
            start_str = a.get("startTimeLocal", "2000-01-01")[:10]
            try:
                act_date = date.fromisoformat(start_str)
            except ValueError:
                continue
                
            days_ago = (today - act_date).days
            if days_ago < 0 or days_ago > 28:
                continue
                
            dist_km = (a.get("distance") or 0) / 1000.0
            if days_ago <= 7:
                acute_km += dist_km
                if days_ago <= 10:
                    print(f"{start_str} | {dist_km:.2f} km | {a.get('activityName')}")
            else:
                if days_ago <= 10:
                    print(f"{start_str} | {dist_km:.2f} km | {a.get('activityName')}")
            chronic_km += dist_km
            
        print("\n--- ACWR CALCULATION ---")
        chronic_avg = chronic_km / 4.0
        acwr = acute_km / chronic_avg if chronic_avg > 0 else 0.0
        print(f"Acute Load (7d): {acute_km:.2f} km")
        print(f"Chronic Load (28d): {chronic_km:.2f} km -> {chronic_avg:.2f} km/wk")
        print(f"ACWR: {acwr:.3f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
