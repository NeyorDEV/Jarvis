import uiautomation as auto
import sys
import re
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

deezer_ctrl = auto.Control(searchDepth=1, Name="Deezer", ClassName="Chrome_WidgetWin_1")
if not deezer_ctrl.Exists(1.0):
    print("Deezer window not found.")
    sys.exit(1)

tracks = []
def find_tracks(ctrl):
    if ctrl.ControlTypeName == "CustomControl" and ctrl.Name and "Écouter" in ctrl.Name:
        tracks.append(ctrl.Name)
    for child in ctrl.GetChildren():
        find_tracks(child)

find_tracks(deezer_ctrl)

print(f"Found {len(tracks)} visible tracks:")
date_pattern = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')
parsed_dates = []

for idx, t in enumerate(tracks):
    dates = date_pattern.findall(t)
    print(f"Track {idx}: Date(s)={dates} -> Name='{t}'")
    if dates:
        try:
            # Parse the first found date
            parsed_dates.append(datetime.strptime(dates[0], "%d/%m/%m")) # Wait, %m is month, %d is day, %Y is year
        except Exception as e:
            pass

# Let's write a parser using datetime
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except:
        return None

dates_parsed = [parse_date(d) for t in tracks for d in date_pattern.findall(t) if parse_date(d)]
print(f"Parsed dates: {[d.strftime('%Y-%m-%d') for d in dates_parsed]}")

if len(dates_parsed) >= 2:
    # Check if ascending or descending
    # Let's find first unique dates to see the trend
    unique_dates = []
    for d in dates_parsed:
        if not unique_dates or unique_dates[-1] != d:
            unique_dates.append(d)
    print(f"Unique sequential dates: {[d.strftime('%Y-%m-%d') for d in unique_dates]}")
    
    is_ascending = True
    is_descending = True
    for i in range(len(unique_dates) - 1):
        if unique_dates[i] < unique_dates[i+1]:
            is_descending = False
        elif unique_dates[i] > unique_dates[i+1]:
            is_ascending = False
            
    print(f"Is ascending (chrono): {is_ascending}")
    print(f"Is descending (dechrono): {is_descending}")
