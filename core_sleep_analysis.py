"""
core_sleep_analysis.py
Fetches sleep data from Garmin Connect for the past 14 days,
analyzes sleep stages (Deep, Light, REM, Awake), and outputs a summary report.
"""
import os, sys
from dotenv import load_dotenv
from garminconnect import Garmin
from datetime import date, timedelta
import json

# Load environment variables
load_dotenv()
GARMIN_EMAIL = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")
TOKEN_STORE = os.path.expanduser("~/.garminconnect")

def analyze_sleep():
    try:
        # Initialize client
        client = Garmin(email=GARMIN_EMAIL, password=GARMIN_PASSWORD)
        client.login(TOKEN_STORE)
        
        # Calculate date range
        today = date.today()
        start_date = today - timedelta(days=14)
        
        print(f"=== SLEEP ANALYSIS ({start_date} to {today}) ===")
        print("Fetching data from Garmin...\n")
        
        # Fetch sleep data
        sleep_data = []
        for i in range(14, -1, -1):
            d = today - timedelta(days=i)
            data = client.get_sleep_data(d.isoformat())
            if data:
                sleep_data.append(data)
        
        if not sleep_data:
            print("No sleep data found in this date range.")
            return

        total_days = len(sleep_data)
        total_score = 0
        total_duration_sec = 0
        total_deep_sec = 0
        total_light_sec = 0
        total_rem_sec = 0
        total_awake_sec = 0
        
        valid_score_days = 0

        print(f"{'Date':<12} | {'Score':<5} | {'Duration':<8} | {'Deep':<6} | {'Light':<6} | {'REM':<6} | {'Awake':<6}")
        print("-" * 65)

        for day in reversed(sleep_data):
            daily_sleep = day.get('dailySleepDTO', {})
            date_str = daily_sleep.get('calendarDate', 'Unknown')
            
            # Garmin provides durations in seconds
            val = daily_sleep
            duration = val.get('sleepTimeSeconds', 0)
            deep = val.get('deepSleepSeconds', 0)
            light = val.get('lightSleepSeconds', 0)
            rem = val.get('remSleepSeconds', 0)
            awake = val.get('awakeSleepSeconds', 0)
            
            # Overall score
            score = val.get('sleepScores', {}).get('overall', {}).get('value')
            
            if score is not None:
                total_score += score
                valid_score_days += 1
                
            total_duration_sec += duration
            total_deep_sec += deep
            total_light_sec += light
            total_rem_sec += rem
            total_awake_sec += awake
            
            # Formatting helpers
            def fmt_hr_min(seconds):
                if not seconds: return "0h 0m"
                h = seconds // 3600
                m = (seconds % 3600) // 60
                return f"{h}h {m:02d}m"
            
            score_str = str(score) if score is not None else "N/A"
            print(f"{date_str:<12} | {score_str:<5} | {fmt_hr_min(duration):<8} | {fmt_hr_min(deep):<6} | {fmt_hr_min(light):<6} | {fmt_hr_min(rem):<6} | {fmt_hr_min(awake):<6}")
            
        print("-" * 65)
        
        # Averages
        if total_days > 0:
            avg_duration = total_duration_sec / total_days
            avg_deep = total_deep_sec / total_days
            avg_light = total_light_sec / total_days
            avg_rem = total_rem_sec / total_days
            avg_awake = total_awake_sec / total_days
            avg_score = (total_score / valid_score_days) if valid_score_days > 0 else "N/A"
            
            # Formatting averages
            def fmt_avg(seconds):
                h = int(seconds // 3600)
                m = int((seconds % 3600) // 60)
                return f"{h}h {m:02d}m"
            
            # Percentages
            pct_deep = (avg_deep / avg_duration) * 100 if avg_duration > 0 else 0
            pct_light = (avg_light / avg_duration) * 100 if avg_duration > 0 else 0
            pct_rem = (avg_rem / avg_duration) * 100 if avg_duration > 0 else 0
            pct_awake = (avg_awake / (avg_duration + avg_awake)) * 100 if (avg_duration + avg_awake) > 0 else 0
            
            print(f"\n=== 14-DAY AVERAGES ===")
            print(f"Days Logged : {total_days}")
            print(f"Avg Score   : {avg_score if isinstance(avg_score, str) else f'{avg_score:.1f}'}")
            print(f"Avg Duration: {fmt_avg(avg_duration)}")
            print(f"Avg Deep    : {fmt_avg(avg_deep)} ({pct_deep:.1f}%) -- [Target: 15-25%]")
            print(f"Avg Light   : {fmt_avg(avg_light)} ({pct_light:.1f}%) -- [Target: 50-60%]")
            print(f"Avg REM     : {fmt_avg(avg_rem)} ({pct_rem:.1f}%) -- [Target: 20-25%]")
            print(f"Avg Awake   : {fmt_avg(avg_awake)} ({pct_awake:.1f}%)")
            
            print("\n=== INSIGHTS ===")
            if isinstance(avg_score, (int, float)):
                if avg_score >= 80:
                    print(" Overall Sleep Quality is EXCELLENT. Recovery is optimized.")
                elif avg_score >= 70:
                    print(" Overall Sleep Quality is GOOD. Adequate for maintenance.")
                else:
                    print(" Overall Sleep Quality is POOR. Focus on sleep hygiene to prevent CNS fatigue.")
                    
            if pct_deep < 15:
                print(" WARNING: Deep sleep is low. This restricts physical (muscular) recovery.")
                print("  -> Fix: Avoid late meals, reduce room temperature, or delay evening workouts.")
            elif pct_deep > 25:
                print(" EXCELLENT: Deep sleep is high. Outstanding physical recovery.")
                
            if pct_rem < 20:
                print(" WARNING: REM sleep is low. This restricts cognitive recovery and CNS repair.")
                print("  -> Fix: Maintain consistent wake times, reduce evening screen time.")
                
            if pct_awake > 10:
                print(" WARNING: High awake time/restlessness detected. Sleep fragmentation is occurring.")

    except Exception as e:
        print(f"Error fetching sleep data: {e}")

if __name__ == "__main__":
    analyze_sleep()
