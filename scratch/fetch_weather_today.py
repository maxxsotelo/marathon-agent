"""
fetch_weather_today.py
Fetches weather for Metro Manila / Marikina for today with a timeout.
"""
import urllib.request
import json
import socket

try:
    url = "https://wttr.in/Marikina?format=j1"
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
    response = urllib.request.urlopen(req, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    
    # data['weather'][0] is today
    today = data['weather'][0]
    date = today['date']
    hourly = today['hourly']
    
    print(f"Weather Forecast for Marikina - {date}")
    for h in hourly:
        time = int(h['time'])
        if time in [1200, 1500, 1800, 2100]: # Afternoon and evening
            chance_of_rain = h['chanceofrain']
            desc = h['weatherDesc'][0]['value']
            temp = h['tempC']
            print(f"Time: {time:04d} | Temp: {temp}C | Rain Chance: {chance_of_rain}% | {desc}")
            
except socket.timeout:
    print("Weather API timed out.")
except Exception as e:
    print(f"Failed to fetch weather: {e}")
