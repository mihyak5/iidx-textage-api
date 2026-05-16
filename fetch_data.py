import requests
import chompjs
import json
import re
import os

def fetch_and_clean_data():
    print("getting textage data...")
    url = "http://textage.cc/score/titletbl.js"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    
    response.encoding = 'shift_jis'
    js_text = response.text

    match = re.search(r'titletbl\s*=\s*(\[.*?\]);', js_text, re.DOTALL)
    
    if match:
        raw_js_array = match.group(1)
        clean_data = chompjs.parse_js_object(raw_js_array)
        
        with open("titletbl.json", "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
            
        print(f"save {len(clean_data)} data ")
    else:
        print("error")

if __name__ == "__main__":
    fetch_and_clean_data()
