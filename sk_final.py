import requests
import base64
import json
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- CONFIGURATION ---
BASE_URL = "https://sufyanpromax.space"
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
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

def convert_utc_to_ist(utc_time_str):
    """ Converts '11:30:00' (UTC) to '05:00 PM' (IST) """
    try:
        if not utc_time_str: return ""
        # Parse the server time
        utc_time = datetime.strptime(utc_time_str, "%H:%M:%S")
        # Add 5 hours and 30 minutes
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        # Format nicely (e.g., 05:00 PM)
        return ist_time.strftime("%I:%M %p")
    except:
        return utc_time_str # Fallback to original if error

def fetch_match_streams(event_data):
    entries = []
    
    # --- 1. Info & Time Conversion ---
    event_name = event_data.get('eventName', 'Cricket Match')
    team_a = event_data.get('teamAName', '')
    team_b = event_data.get('teamBName', '')
    raw_time = event_data.get('time', '') # Server gives "11:30:00"
    
    # Convert to IST
    ist_time = convert_utc_to_ist(raw_time) # Becomes "05:00 PM"
    
    # Group Title: "ICC T20 World Cup Warm-up 05:00 PM"
    group_title = f"{event_name} {ist_time}".strip()
    
    if team_a and team_b:
        channel_name = f"{team_a} vs {team_b}"
    else:
        channel_name = event_name

    logo = event_data.get('eventLogo', '')
    link_path = event_data.get('links')
    
    if not link_path: return []

    full_url = f"{BASE_URL}/{link_path}"
    print(f"   ⚡ Fetching: {channel_name} ({group_title})")
    
    try:
        res = requests.get(full_url, headers=HEADERS, timeout=10)
        decrypted_streams = decrypt_sk_tech(res.text) if res.status_code == 200 else None
        
        if not decrypted_streams: return []

        # --- 2. Parse Streams ---
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

        # --- 3. Build M3U Entry ---
        for idx, item in enumerate(stream_list):
            if not isinstance(item, dict):
                 item = {"link": str(item), "title": f"Link {idx+1}"}

            stream_url = item.get('link') or item.get('url')
            if not stream_url: continue
            
            stream_variant = item.get('title') or item.get('name') or f"Link {idx+1}"
            drm_key = item.get('api', '')
            
            # Start Entry with GROUP-TITLE
            entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title}", {channel_name} ({stream_variant})\n'
            
            # DRM Tags
            if drm_key and len(str(drm_key)) > 10:
                entry += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_key}\n'

            # Headers
            entry += f'#EXTVLCOPT:http-user-agent={APP_UA}\n'
            final_url = f"{stream_url}|User-Agent={APP_UA}&Referer={BASE_URL}/"
            
            entry += f"{final_url}\n"
            entries.append(entry)

    except Exception as e:
        print(f"      ❌ Error: {e}")

    return entries

def main():
    print("🚀 Starting SK Live (IST Time Fix)...")
    all_entries = []
    
    try:
        res = requests.get(f"{BASE_URL}/events.txt", headers=HEADERS, timeout=15)
        raw_data = decrypt_sk_tech(res.text)
        
        if not raw_data: 
            print("❌ Failed to decrypt main list")
            return

        wrapper_list = json.loads(raw_data)
        print(f"📋 Found {len(wrapper_list)} total events.")
        
        cricket_count = 0
        for wrapper in wrapper_list:
            event_str = wrapper.get('event')
            if not event_str: continue
            
            try:
                event = json.loads(event_str)
                cat = event.get('category', '').strip().lower()
                name = event.get('eventName', '').strip().lower()
                
                # Filter: Cricket Only
                if 'cricket' in cat or 'cricket' in name:
                    cricket_count += 1
                    match_entries = fetch_match_streams(event)
                    all_entries.extend(match_entries)
            except:
                continue

        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if all_entries:
                for entry in all_entries:
                    f.write(entry)
                print(f"🎉 Playlist Updated! Found {cricket_count} cricket matches.")
            else:
                print("⚠️ No cricket matches found.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
