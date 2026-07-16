import requests
import re

query = "chats"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "fr,fr-FR;q=0.9,en;q=0.8",
    "Referer": "https://duckduckgo.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest"
}

try:
    print(f"Requesting DDG main page for: {query}")
    r = requests.get(
        "https://duckduckgo.com/",
        params={"q": query, "iax": "images", "ia": "images"},
        headers=headers, timeout=8
    )
    print(f"Status Code 1: {r.status_code}")
    vqd_match = re.search(r'vqd=([\d-]+)', r.text)
    if vqd_match:
        vqd = vqd_match.group(1)
        print(f"Found vqd: {vqd}")
        
        # Request images API
        r2 = requests.get(
            "https://duckduckgo.com/i.js",
            params={"l": "fr-fr", "o": "json", "q": query, "vqd": vqd, "f": ",,,,,", "p": "1"},
            headers=headers, timeout=8
        )
        print(f"Status Code 2: {r2.status_code}")
        print(f"Content Type: {r2.headers.get('Content-Type')}")
        print(f"Response snippet: {r2.text[:200]}")
    else:
        print("vqd not found in main page!")
except Exception as e:
    print(f"Error: {e}")
