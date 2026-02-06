import requests
import re
import urllib.parse

# Official Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Referer": "https://run-machine.pages.dev/"
}

def final_extraction_test():
    url = "https://allrounderlive.pages.dev/dilz?id=65656576"
    print(f"📡 Fetching Page: {url}")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        html = res.text
        
        # 1. Screenshot 156716.jpg ke mutabiq array extract karein
        # Hum specifically _0x477048 ya kisi bhi bade array ko dhoond rahe hain
        array_match = re.search(r"var\s+(_0x\w+)\s*=\s*\[(.*?)\]", html)
        
        if array_match:
            print(f"✅ Found Obfuscated Array: {array_match.group(1)}")
            raw_data = array_match.group(2)
            
            # 2. Pieces ko jodo (Quotes aur commas hata kar)
            pieces = raw_data.replace("'", "").replace('"', "").replace(" ", "").split(",")
            full_blob = "".join(pieces)
            
            # 3. Apply Official Fix: '0%' -> '%'
            # Jaisa screenshot 156716 me dikh raha hai (0%20, 0%23)
            cleaned = full_blob.replace('0%', '%')
            
            # 4. URL Decode
            decoded = urllib.parse.unquote(cleaned)
            print("🔓 Data Decoded Successfully.")
            
            # 5. Search for AWS IVS pattern (Toolkit Style)
            aws_match = re.search(r'(https?://[^"\'\s]*?playback\.live-video\.net[^"\'\s]*?\.m3u8[^"\'\s]*)', decoded)
            
            if aws_match:
                print(f"\n🎉🎉 BINGO! AWS LINK FOUND:\n{aws_match.group(1)}")
            else:
                # Agar pattern na mile to pura decoded text scan karo m3u8 ke liye
                gen_match = re.search(r'(https?://[^\s"\'<>]*?\.m3u8[^\s"\'<>]*?)', decoded)
                if gen_match:
                    print(f"\n🎉 GENERIC M3U8 FOUND:\n{gen_match.group(1)}")
                else:
                    print("❌ Link pattern nahi mila. Decoded snippet:")
                    print(decoded[:300])
        else:
            print("❌ Page me koi obfuscated array nahi mila.")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    final_extraction_test()
