import requests
import json
import time

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 45.2933, "longitude": 4.1728,
    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weathercode",
    "daily": "temperature_2m_max,temperature_2m_min",
    "timezone": "auto", "forecast_days": 1
}

# 1. Test without headers (simulating the old behaviour)
print("Testing request WITHOUT User-Agent headers...")
try:
    t0 = time.time()
    r = requests.get(url, params=params, timeout=10)
    print(f"Without headers: Status {r.status_code}, time={time.time()-t0:.2f}s")
    if r.status_code == 200:
        print("Success without headers!")
except Exception as e:
    print(f"Failed without headers: {e}")

# 2. Test WITH headers (new behaviour)
print("\nTesting request WITH User-Agent headers...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}
try:
    t0 = time.time()
    r = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"With headers: Status {r.status_code}, time={time.time()-t0:.2f}s")
    if r.status_code == 200:
        print("Success with headers!")
        print("Weather info:", json.dumps(r.json().get("current"), indent=2))
except Exception as e:
    print(f"Failed with headers: {e}")
