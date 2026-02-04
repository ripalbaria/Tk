import requests
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- CONFIGURATION ---
BASE_URL = "https://sufyanpromax.space"
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"

# Headers
APP_UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
HEADERS = {
    "User-Agent": APP_UA,
    "Connection": "keep-alive"
}

LOOKUP_TABLE = (
    "\u0000\u0001\u0002\u0003\u0004\u0005\u0006\u0007\x08\t\n\u000b\u000c\r\u000e\u000f"
    "\u0010\u0011\u0012\u0013\u0014\u0015\u0016\u0017\x18\x19\x1a\u001b\u001c\u001d\u001e\u001f"
    " !\"#$%&'()*+,-./"
    "0123456789:;<=>?"
    "@EGMNKABUVCDYHLI"
    "FPOZQSRWTXJ[\\]^_"
    "`egmnkabuvcdyhli"
    "fpozqsrwtxj{|}~\x7f"
)

def decrypt_sk_tech(encrypted_text):
    if not encrypted_text: return None
    try:
        mapped = "".join([LOOKUP_TABLE[ord(c)] if ord(c) < len(LOOKUP_TABLE) else c for c in encrypted_text])
        decoded_str = base64.b64decode(mapped).decode('utf-8')[::-1]
        ciphertext = base64.b64decode(decoded_str)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
    except:
        return None

def fetch_match_streams(event_data):
    entries = []
    
    event_name = event_data.get('eventName', 'Cricket Match')
    team_a = event_data.get('teamAName', '')
    team_b = event_data.get('teamBName', '')
    title = f"{team_a} vs {team_b} - {event_name}" if team_a and team_b else event_name
    logo = event_data.get('eventLogo', '')
    link_path = event_data.get('links')
    
    if not link_path: return []

    full_url = f"{BASE_URL}/{link_path}"
    print(f"   ⚡ Processing: {title}")
    
    try:
        res = requests.get(full_url, headers=HEADERS, timeout=10)
        decrypted_streams = decrypt_sk_tech(res.text) if res.status_code == 200 else None
        
        if not decrypted_streams: return []

        # Parse Stream Data
        stream_list = []
        try:
            parsed = json.loads(decrypted_streams)
            if isinstance(parsed, dict): 
                stream_list = parsed.get('streamUrls', [])
            elif isinstance(parsed, list):
                stream_list = parsed
            else:
                if "http" in decrypted_streams:
                    stream_list = [{"link": decrypted_streams.strip(), "title": "Direct Stream"}]
        except:
            if "http" in decrypted_streams:
                stream_list = [{"link": decrypted_streams.strip(), "title": "Direct Stream"}]

        # Process each stream
        for idx, item in enumerate(stream_list):
            if not isinstance(item, dict):
                 item = {"link": str(item), "title": f"Link {idx+1}"}

            stream_url = item.get('link') or item.get('url')
            if not stream_url: continue
            
            stream_name = item.get('title') or item.get('name') or f"Link {idx+1}"
            
            # --- EXTRACT KEY & SCHEME FROM 'api' FIELD ---
            # Based on your Termux output: "api" contains the key
            drm_key = item.get('api', '')
            
            # Start Entry
            entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="Cricket", {title} ({stream_name})\n'
            
            # If 'api' field has data (length > 10), treat it as a Key
            if drm_key and len(str(drm_key)) > 10:
                # 99% of the time, this is ClearKey based on your screenshot
                entry += '#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n'
                entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_key}\n'

            # Standard Headers
            entry += f'#EXTVLCOPT:http-user-agent={APP_UA}\n'
            entry += f"{stream_url}|User-Agent={APP_UA}&Referer={BASE_URL}/\n"
            
            entries.append(entry)

    except Exception as e:
        print(f"      ❌ Error: {e}")

    return entries

def main():
    print("🚀 Starting SK Live (API Field Fix)...")
    all_entries = []
    
    try:
        res = requests.get(f"{BASE_URL}/events.txt", headers=HEADERS, timeout=15)
        raw_data = decrypt_sk_tech(res.text)
        if not raw_data: return

        wrapper_list = json.loads(raw_data)
        
        for wrapper in wrapper_list:
            event_str = wrapper.get('event')
            if not event_str: continue
            
            try:
                event = json.loads(event_str)
                cat = event.get('category', '').strip().lower()
                name = event.get('eventName', '').strip().lower()
                
                # Broad filter
                if any(x in cat or x in name for x in ['cricket', 'ipl', 't20', 'live']):
                    all_entries.extend(fetch_match_streams(event))
            except:
                continue

        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for entry in all_entries:
                f.write(entry)
        
        print(f"🎉 Playlist Updated! Saved {len(all_entries)} streams.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
