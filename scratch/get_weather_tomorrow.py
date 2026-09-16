"""
get_weather_tomorrow.py
Fetches weather for Metro Manila / Marikina for tomorrow to check rain probabilities.
"""
import urllib.request
import json

try:
    url = "https://wttr.in/Marikina?format=j1"
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    
    # data['weather'] is an array of days. 0 is today, 1 is tomorrow.
    tomorrow = data['weather'][1]
    date = tomorrow['date']
    hourly = tomorrow['hourly']
    
    print(f"Weather Forecast for Marikina - {date}")
    for h in hourly:
        time = int(h['time'])
        if time in [600, 900, 1500, 1800]: # Morning and afternoon/evening running times
            chance_of_rain = h['chanceofrain']
            desc = h['weatherDesc'][0]['value']
            temp = h['tempC']
            print(f"Time: {time:04d} | Temp: {temp}C | Rain Chance: {chance_of_rain}% | {desc}")
            
except Exception as e:
    print(f"Failed to fetch weather: {e}")
