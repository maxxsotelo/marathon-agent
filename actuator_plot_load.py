import os, json
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from garminconnect import Garmin
import matplotlib.pyplot as plt

load_dotenv()
try:
    client = Garmin(os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD"))
    client.login()
    
    activities = client.get_activities(0, 50)
    today = datetime.today()
    three_weeks_ago = today - timedelta(days=21)
    
    loads = {}
    for act in activities:
        start_str = act.get('startTimeLocal', '')[:10]
        if not start_str: continue
        try:
            dt = datetime.strptime(start_str, "%Y-%m-%d")
            if dt >= three_weeks_ago:
                load = act.get('activityTrainingLoad', 0)
                if load is None: load = 0
                loads[start_str] = loads.get(start_str, 0) + load
        except:
            pass
            
    dates = sorted(loads.keys())
    values = [loads[d] for d in dates]
    
    plt.figure(figsize=(10, 5))
    plt.bar(dates, values, color='skyblue')
    plt.title('Training Load (Last 3 Weeks)')
    plt.xlabel('Date')
    plt.ylabel('Training Load')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('training_load.png')
    print("Plot saved to training_load.png")
except Exception as e:
    print(f"Error: {e}")
