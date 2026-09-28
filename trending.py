import re
import json

import requests

def extract_trends_from_html(html_text):
    # 1. Use Regex to find the hidden 'ds:0' data payload
    # We look for the data array just before 'sideChannel'
    match = re.search(r"AF_initDataCallback\(\{key: 'ds:0'.*?data:(\[.*?\]), sideChannel:", html_text)
    
    if not match:
        print("Could not find trending data in the HTML.")
        return None
        
    # 2. Extract the raw JSON string
    raw_json_string = match.group(1)
    
    try:
        # 3. Convert the string into a Python list
        data = json.loads(raw_json_string)
        
        # 4. In Google's structure, the actual trends are inside index 1
        trends_list = data[1]
        
        extracted_trends = []
        for trend in trends_list:
            keyword = trend[0]
            # Search volume is usually at index 6 in this specific payload
            search_volume = trend[6] if len(trend) > 6 else "Unknown"
            
            extracted_trends.append({
                "keyword": keyword,
                "volume": search_volume,
                "volume_label": _volume_label(search_volume),
            })
            
        return extracted_trends
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        return None

def _volume_label(volume):
    try:
        count = int(volume)
    except (TypeError, ValueError):
        return "Unknown"
    if count >= 1_000_000:
        return f"{count // 1_000_000}M+"
    if count >= 1_000:
        return f"{count // 1_000}K+"
    return str(count)


def get_top_trends(geo="IN", limit=5):
    url = f"https://trends.google.com/trending?geo={geo}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    trends = extract_trends_from_html(response.text) or []
    return trends[:limit]
