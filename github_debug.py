import requests
import subprocess
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Referer": "https://run-machine.pages.dev/"
}

def run_debug():
    url = "https://allrounderlive.pages.dev/dilz?id=65656576"
    print(f"📡 Fetching: {url}")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        # Page ko save karein taaki Node use padh sake
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(res.text)
        
        # Node.js ko execute karein
        print("🕵️ Executing Decoder...")
        # Check karein ki logic.js repo ki root me hai
        result = subprocess.run(['node', 'logic.js'], capture_output=True, text=True)
        
        if result.stdout.strip():
            print(f"✅ RESULT: {result.stdout.strip()}")
        else:
            print("❌ No link extracted.")
            if result.stderr: print(f"Stderr: {result.stderr}")
            
    except Exception as e:
        print(f"💥 Python Error: {e}")

if __name__ == "__main__":
    run_debug()
