import requests
import re
import urllib.parse

# Headers to mimic official request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Referer": "https://run-machine.pages.dev/"
}

def final_extraction():
    # Targeted ID from your JSON dump
    url = "https://allrounderlive.pages.dev/dilz?id=65656576"
    print(f"📡 Fetching Page: {url}")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        html = res.text
        
        # 1. Screenshot 156716.jpg ke mutabiq array extract karein
        array_match = re.search(r"var\s+_0x477048\s*=\s*\[(.*?)\]", html)
        
        if array_match:
            print("✅ Found Obfuscated Array: _0x477048")
            raw_data = array_match.group(1)
            
            # 2. Pieces ko jodo (Quotes aur commas hata kar)
            pieces = raw_data.replace("'", "").replace('"', "").replace(" ", "").split(",")
            full_blob = "".join(pieces)
            
            # 3. Apply Official Fix: '0%' -> '%' (Based on your screenshot snippet)
            cleaned = full_blob.replace('0%', '%')
            
            # 4. URL Decode (Standard unquote)
            decoded = urllib.parse.unquote(cleaned)
            print("🔓 Data Decoded Successfully.")
            
            # 5. Search for AWS IVS link (Toolkit style pattern)
            aws_match = re.search(r'(https?://[^"\'\s]*?playback\.live-video\.net[^"\'\s]*?\.m3u8[^"\'\s]*)', decoded)
            
            if aws_match:
                print(f"\n🎉🎉 BINGO! AWS LINK FOUND:\n{aws_match.group(1)}")
            else:
                # Fallback: Agar token bikhra ho toh generic search
                gen_match = re.search(r'(https?://[^\s"\'<>]*?\.m3u8[^\s"\'<>]*?)', decoded)
                if gen_match:
                    print(f"\n🎉 GENERIC M3U8 FOUND:\n{gen_match.group(1)}")
                else:
                    print("❌ Link pattern nahi mila. Decoded snippet:")
                    print(decoded[:400])
        else:
            print("❌ Page me array '_0x477048' nahi mila.")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    final_extraction()
