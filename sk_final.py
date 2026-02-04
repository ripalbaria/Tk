import requests
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- CONFIGURATION ---
BASE_URL = "https://sufyanpromax.space"
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"

# Headers mimicking the app
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
    
    # 1. Event Metadata
    event_name = event_data.get('eventName', 'Cricket Match')
    team_a = event_data.get('teamAName', '')
    team_b = event_data.get('teamBName', '')
    
    if team_a and team_b:
        title = f"{team_a} vs {team_b} - {event_name}"
    else:
        title = event_name
        
    logo = event_data.get('eventLogo', '')
    link_path = event_data.get('links')
    
    if not link_path: return []

    full_url = f"{BASE_URL}/{link_path}"
    print(f"   ⚡ Processing: {title}")
    
    try:
        res = requests.get(full_url, headers=HEADERS, timeout=10)
        if res.status_code != 200: return []
            
        decrypted_streams = decrypt_sk_tech(res.text)
        if not decrypted_streams: return []

        # 2. Parse Stream Data
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

        # 3. Build M3U Entry
        for idx, item in enumerate(stream_list):
            if not isinstance(item, dict):
                 item = {"link": str(item), "title": f"Link {idx+1}"}

            stream_url = item.get('link') or item.get('url')
            if not stream_url: continue
            
            stream_name = item.get('title') or item.get('name') or f"Link {idx+1}"
            
            # --- CLEARKEY LOGIC ---
            drm_scheme = item.get('drmScheme', '').lower()
            drm_license = item.get('drmLicense', '')
            
            # Auto-detect ClearKey if keys match standard JSON format
            if 'clearkey' in drm_scheme or 'clearkey' in str(drm_license).lower() or (drm_license and "{" in drm_license):
                is_clearkey = True
            else:
                is_clearkey = False

            # Start Entry
            entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="Cricket", {title} ({stream_name})\n'
            
            if is_clearkey and drm_license:
                entry += '#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey\n'
                
                # Handle JSON format keys {"keys":[{"k":"...","kid":"..."}]} -> kid:k
                if "{" in drm_license:
                    try:
                        key_data = json.loads(drm_license)
                        if "keys" in key_data:
                            kid = key_data["keys"][0]["kid"]
                            k = key_data["keys"][0]["k"]
                            entry += f'#KODIPROP:inputstream.adaptive.license_key={kid}:{k}\n'
                        else:
                             # Fallback if structure is different
                             entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
                    except:
                         # If JSON parse fails, just use raw string
                         entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
                else:
                    # Already in kid:key format
                    entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
            
            # VLC Headers (Just in case)
            entry += f'#EXTVLCOPT:http-user-agent={APP_UA}\n'
            
            # Pipe Syntax (Crucial for playback)
            final_url = f"{stream_url}|User-Agent={APP_UA}&Referer={BASE_URL}/"
            
            entry += f"{final_url}\n"
            entries.append(entry)

    except Exception as e:
        print(f"      ❌ Error: {e}")

    return entries

def main():
    print("🚀 Starting SK Live (ClearKey Edition)...")
    all_entries = []
    
    try:
        res = requests.get(f"{BASE_URL}/events.txt", headers=HEADERS, timeout=15)
        raw_data = decrypt_sk_tech(res.text)
        
        if not raw_data: return

        wrapper_list = json.loads(raw_data)
        print(f"📋 Scanning {len(wrapper_list)} events...")
        
        for wrapper in wrapper_list:
            event_str = wrapper.get('event')
            if not event_str: continue
            
            try:
                event = json.loads(event_str)
                cat = event.get('category', '').strip().lower()
                name = event.get('eventName', '').strip().lower()
                
                # Filter for Cricket
                if 'cricket' in cat or 'cricket' in name or 'ipl' in name or 't20' in name:
                    match_entries = fetch_match_streams(event)
                    all_entries.extend(match_entries)
            except:
                continue

        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if all_entries:
                for entry in all_entries:
                    f.write(entry)
                print(f"🎉 Playlist Updated with {len(all_entries)} ClearKey streams!")
            else:
                print("⚠️ No live cricket matches found.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
