import requests
import subprocess
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Referer": "https://run-machine.pages.dev/"
}

def run_debug():
    # ID from your JSON dump for Star Sports Hindi
    url = "https://allrounderlive.pages.dev/dilz?id=65656576"
    print(f"📡 Requesting Source: {url}")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(res.text)
        
        print("🕵️ Executing Hybrid Decoder...")
        # Running Node.js as a subprocess
        result = subprocess.run(['node', 'logic.js'], capture_output=True, text=True)
        
        if result.stdout.strip():
            print(f"✅ FINAL EXTRACTED LINK: {result.stdout.strip()}")
        else:
            print("❌ Extraction failed. Check decoded snippet below:")
            print(result.stderr)
            
    except Exception as e:
        print(f"💥 Python Error: {e}")

if __name__ == "__main__":
    run_debug()
