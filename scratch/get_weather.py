import urllib.request
import json

# Coordinates for Marikina / Concepcion Uno area
lat = 14.65
lon = 121.10

url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Asia%2FSingapore"

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        precip = daily.get("precipitation_probability_max", [])
        weather_code = daily.get("weather_code", [])
        
        # WMO Weather interpretation codes
        codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 71: "Slight snow fall",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with light hail", 99: "Thunderstorm with heavy hail"
        }
        
        for i, date in enumerate(dates):
            if i > 3: break # Only show next few days
            code_desc = codes.get(weather_code[i], "Unknown")
            print(f"Date: {date} | Precip Prob: {precip[i]}% | Condition: {code_desc}")
except Exception as e:
    print(f"Error fetching weather: {e}")
