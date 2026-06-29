import os
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
from garminconnect import Garmin

load_dotenv()
email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")

TOKEN_STORE = os.path.expanduser("~/.garminconnect")

def parse_week(activities):
    """Extracts and sums all relevant metrics from a list of Garmin activities."""
    data = {
        'run_dist': 0.0,
        'walk_dist': 0.0,
        'longest_run': 0.0,
        'run_elev': 0.0,
        'run_time': 0.0,
        'walk_time': 0.0,
        'bike_dist': 0.0,
        'strength': False,
        'run_sessions': 0,
        'strength_count': 0,
        'hr_sum': 0.0,
        'hr_count': 0,
    }
    
    if not activities:
        return data

    for act in activities:
        act_type = act.get('activityType', {}).get('typeKey', '')
        dist_km = (act.get('distance') or 0) / 1000
        dur_sec = act.get('duration') or 0
        elev_m = act.get('elevationGain') or 0
        avg_hr = act.get('averageHR') or 0
        
        if act_type == 'running':
            data['run_dist'] += dist_km
            data['run_time'] += dur_sec
            data['run_elev'] += elev_m
            data['run_sessions'] += 1
            if avg_hr > 0:
                data['hr_sum'] += avg_hr
                data['hr_count'] += 1
            if dist_km > data['longest_run']:
                data['longest_run'] = dist_km
                
        elif act_type == 'walking':
            data['walk_dist'] += dist_km
            data['walk_time'] += dur_sec
            
        elif act_type == 'cycling':
            data['bike_dist'] += dist_km
            
        elif act_type == 'strength_training':
            data['strength'] = True
            # Only count towards the 2x/week target if it's a substantive session (> 15 minutes)
            if dur_sec >= 900:
                data['strength_count'] += 1
            
    return data

def format_time(seconds):
    if seconds == 0: return "0:00:00"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}"

def get_pace(seconds, distance_km):
    if distance_km == 0: return "0:00"
    pace_sec = seconds / distance_km
    m = int(pace_sec // 60)
    s = int(pace_sec % 60)
    return f"{m}:{s:02d}"

def calc_change(current, previous):
    if previous == 0:
        return "+100.0%" if current > 0 else "0.0%"
    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"

def run_rolling_audit(num_weeks=3):
    try:
        client = Garmin(
            email=email,
            password=password,
            prompt_mfa=lambda: input("Garmin MFA code: "),
        )
        client.login(TOKEN_STORE)
        
        # Dynamically calculate the last completed Mon-Sun weeks
        today = date.today()
        offset_to_sunday = today.weekday() + 1
        last_sunday = today - timedelta(days=offset_to_sunday)
        
        # Generate the date ranges (we need +1 for the baseline week)
        blocks = []
        for i in range(num_weeks + 1):
            w_end = last_sunday - timedelta(days=i*7)
            w_start = w_end - timedelta(days=6)
            blocks.append((w_start, w_end))
            
        blocks.reverse() # Sort oldest to newest
        
        print(f"=== AUTONOMOUS 3-WEEK BLOCK AUDIT ===\n")
        
        # Loop through the target weeks and compare to the week prior
        for i in range(1, len(blocks)):
            t_start, t_end = blocks[i]
            p_start, p_end = blocks[i-1]
            
            curr_acts = client.get_activities_by_date(t_start.isoformat(), t_end.isoformat())
            curr_data = parse_week(curr_acts)
            
            prev_acts = client.get_activities_by_date(p_start.isoformat(), p_end.isoformat())
            prev_data = parse_week(prev_acts)
            
            # Calculations
            total_mileage = curr_data['run_dist'] + curr_data['walk_dist']
            total_time_sec = curr_data['run_time'] + curr_data['walk_time']
            total_run_pct = calc_change(curr_data['run_dist'], prev_data['run_dist'])
            long_run_pct = calc_change(curr_data['longest_run'], prev_data['longest_run'])
            
            date_label = f"{t_start.strftime('%b %d')}-{t_end.strftime('%d')}"
            
            print(f"--- BLOCK: {date_label} ---")
            print(f"Run Sessions:        {curr_data['run_sessions']}")
            print(f"Run Mileage:         {curr_data['run_dist']:.2f} km ({total_run_pct})")
            print(f"Longest Run:         {curr_data['longest_run']:.2f} km ({long_run_pct})")
            print(f"Total Time:          {format_time(total_time_sec)}")
            print(f"Avg. Pace (Run):     {get_pace(curr_data['run_time'], curr_data['run_dist'])} /km")
            avg_hr = curr_data['hr_sum'] / curr_data['hr_count'] if curr_data['hr_count'] else 0
            print(f"Avg HR (Run):        {avg_hr:.0f} bpm" if avg_hr else "Avg HR (Run):        N/A")
            print(f"Run Elev:            {curr_data['run_elev']:.0f} m")
            print(f"Cross-Train (Bike):  {curr_data['bike_dist']:.2f} km")
            print(f"Strength Sessions:   {curr_data['strength_count']} {'[OK]' if curr_data['strength_count'] >= 2 else '[!! BELOW 2/WEEK TARGET]'}")
            
            # 10% rule check
            if prev_data['run_dist'] > 0:
                pct_change = ((curr_data['run_dist'] - prev_data['run_dist']) / prev_data['run_dist']) * 100
                if pct_change > 10:
                    print(f"10% Rule:            [!! EXCEEDED] {pct_change:+.1f}% week-over-week")
                else:
                    print(f"10% Rule:            [OK] {pct_change:+.1f}% week-over-week")
            print()

        # ── CURRENT (PARTIAL) WEEK ────────────────────────────────────────────
        # Show the current Mon-Today partial week so athlete can see mid-week status
        days_since_monday = today.weekday()  # 0=Mon, 6=Sun
        curr_monday = today - timedelta(days=days_since_monday)
        curr_acts = client.get_activities_by_date(curr_monday.isoformat(), today.isoformat())
        curr_partial = parse_week(curr_acts)
        
        # Use the most recent completed week as the comparison baseline
        last_complete_start, last_complete_end = blocks[-1]
        last_complete_acts = client.get_activities_by_date(last_complete_start.isoformat(), last_complete_end.isoformat())
        last_complete = parse_week(last_complete_acts)
        
        days_elapsed = days_since_monday + 1  # 1 = Monday only, 7 = full week
        projected_km = (curr_partial['run_dist'] / days_elapsed) * 7 if days_elapsed > 0 else 0
        
        print(f"--- CURRENT WEEK (Partial): {curr_monday.strftime('%b %d')}-{today.strftime('%b %d')} ({days_elapsed}/7 days) ---")
        print(f"Run Sessions:        {curr_partial['run_sessions']}")
        print(f"Run Mileage:         {curr_partial['run_dist']:.2f} km")
        print(f"Longest Run:         {curr_partial['longest_run']:.2f} km")
        if curr_partial['run_time'] > 0:
            print(f"Total Time:          {format_time(curr_partial['run_time'] + curr_partial['walk_time'])}")
            print(f"Avg. Pace (Run):     {get_pace(curr_partial['run_time'], curr_partial['run_dist'])} /km")
        avg_hr_p = curr_partial['hr_sum'] / curr_partial['hr_count'] if curr_partial['hr_count'] else 0
        if avg_hr_p:
            print(f"Avg HR (Run):        {avg_hr_p:.0f} bpm")
        print(f"Run Elev:            {curr_partial['run_elev']:.0f} m")
        print(f"Cross-Train (Bike):  {curr_partial['bike_dist']:.2f} km")
        print(f"Strength Sessions:   {curr_partial['strength_count']} {'[OK]' if curr_partial['strength_count'] >= 2 else '[PENDING -- target 2/week]'}")
        if projected_km > 0:
            print(f"Projected Weekly km: {projected_km:.1f} km (if current rate continues)")
            if last_complete['run_dist'] > 0:
                proj_pct = ((projected_km - last_complete['run_dist']) / last_complete['run_dist']) * 100
                print(f"Projected vs Last:   {proj_pct:+.1f}%")
        print()

    except Exception as e:
        print(f"Sync Error: {e}")

if __name__ == "__main__":
    run_rolling_audit(num_weeks=3)