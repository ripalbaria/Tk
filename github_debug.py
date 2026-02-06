import requests
import subprocess
import os

# Official App logic ke mutabiq headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Referer": "https://run-machine.pages.dev/"
}

def test_extraction():
    # 1. Star Sports Hindi ka page load karo
    test_url = "https://allrounderlive.pages.dev/dilz?id=65656576"
    print(f"📡 Fetching: {test_url}")
    
    try:
        res = requests.get(test_url, headers=HEADERS, timeout=15)
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(res.text)
        
        # 2. Node.js script chalao
        print("🕵️ Running Node.js Decoder...")
        result = subprocess.run(['node', 'debug_logic.js'], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
    except Exception as e:
        print(f"💥 Python Error: {e}")

if __name__ == "__main__":
    test_extraction()

