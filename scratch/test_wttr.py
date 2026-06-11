import requests
import json

url = "https://wttr.in/Monistrol-sur-Loire?format=j1"
try:
    r = requests.get(url, timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("Keys in JSON:", list(data.keys()))
        
        # Current condition
        curr = data.get("current_condition", [{}])[0]
        print("\nCurrent condition:")
        print("temp_C:", curr.get("temp_C"))
        print("FeelsLikeC:", curr.get("FeelsLikeC"))
        print("humidity:", curr.get("humidity"))
        print("windspeedKmph:", curr.get("windspeedKmph"))
        print("weatherDesc:", curr.get("weatherDesc", [{}])[0].get("value"))
        
        # Weather (daily)
        weather = data.get("weather", [{}])[0]
        print("\nDaily forecast:")
        print("maxtempC:", weather.get("maxtempC"))
        print("mintempC:", weather.get("mintempC"))
except Exception as e:
    print("Error:", e)
