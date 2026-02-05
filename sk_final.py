from curl_cffi import requests
import base64
import json
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- CONFIGURATION ---
BASE_URL = "https://sufyanpromax.space"
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"

# Decryption Table
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
    try:
        if not utc_time_str: return ""
        utc_time = datetime.strptime(utc_time_str, "%H:%M:%S")
        ist_time = utc_time + timedelta(hours=5, minutes=30)
        return ist_time.strftime("%I:%M %p")
    except:
        return utc_time_str

def resolve_kick_link(api_url, target_key="playback_url"):
    """ Kick Link Resolver using curl_cffi (No Proxy Needed) """
    print(f"      ⚙️ Resolving Kick URL: {api_url}")
    try:
        # Jadu: Chrome Fingerprint use kar rahe hain
        resp = requests.get(
            api_url,
            impersonate="chrome110",
            timeout=15
        )
        
        if resp.status_code == 200:
            data = resp.json()
            video_url = data.get(target_key)
            if video_url:
                print(f"      ✅ Success! Link Found.")
                return video_url
        else:
            print(f"      ⚠️ Failed with Status: {resp.status_code}")
            
    except Exception as e:
        print(f"      ⚠️ Resolver Error: {e}")
    
    return None

def fetch_match_streams(event_data):
    entries = []
    
    event_name = event_data.get('eventName', 'Cricket Match')
    team_a = event_data.get('teamAName', '')
    team_b = event_data.get('teamBName', '')
    raw_time = event_data.get('time', '') 
    ist_time = convert_utc_to_ist(raw_time) 
    group_title = f"{event_name} {ist_time}".strip()
    
    if team_a and team_b:
        channel_name = f"{team_a} vs {team_b}"
    else:
        channel_name = event_name

    logo = event_data.get('eventLogo', '')
    link_path = event_data.get('links')
    
    if not link_path: return []

    full_url = f"{BASE_URL}/{link_path}"
    print(f"   ⚡ Fetching: {channel_name}")
    
    try:
        # Main list fetch karne ke liye bhi fake browser use karenge
        res = requests.get(full_url, impersonate="chrome110", timeout=15)
        decrypted_streams = decrypt_sk_tech(res.text) if res.status_code == 200 else None
        
        if not decrypted_streams: return []

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

        for idx, item in enumerate(stream_list):
            if not isinstance(item, dict):
                 item = {"link": str(item), "title": f"Link {idx+1}"}

            original_link = item.get('link') or item.get('url')
            if not original_link: continue
            
            stream_variant = item.get('title') or item.get('name') or f"Link {idx+1}"
            drm_key = item.get('api', '')
            token_api_data = item.get('tokenApi', '')

            # === KICK RESOLVER LOGIC ===
            final_stream_url = original_link
            
            # Agar TokenApi hai, to resolve karo
            if token_api_data and len(str(token_api_data)) > 10:
                try:
                    t_data = json.loads(token_api_data)
                    k_url = t_data.get("url")
                    k_key = t_data.get("link_key")
                    if k_url and k_key:
                        resolved = resolve_kick_link(k_url, k_key)
                        if resolved:
                            final_stream_url = resolved
                except:
                    pass
            # =======================

            entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_title}", {channel_name} ({stream_variant})\n'
            
            if drm_key and len(str(drm_key)) > 10:
                entry += '#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_key}\n'

            if "hotstar.com" in final_stream_url or "|" in final_stream_url:
                entry += f"{final_stream_url}\n"
            else:
                ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                entry += f"{final_stream_url}|User-Agent={ua}\n"
            
            entries.append(entry)

    except Exception as e:
        print(f"      ❌ Error: {e}")

    return entries

def main():
    print("🚀 Starting SK Live (Direct Curl_CFFI)...")
    all_entries = []
    
    try:
        res = requests.get(f"{BASE_URL}/events.txt", impersonate="chrome110", timeout=15)
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
                
                if 'cricket' in cat or 'cricket' in name:
                    cricket_count += 1
                    match_entries = fetch_match_streams(event)
                    all_entries.extend(match_entries)
            except:
                continue

        # Save Playlist
        utc_now = datetime.utcnow()
        ist_now = utc_now + timedelta(hours=5, minutes=30)
        now_str = ist_now.strftime('%Y-%m-%d %I:%M:%S %p')
        
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"# UPDATED: {now_str} IST\n") 
            f.write(f"# Total Matches: {cricket_count}\n\n")
            
            if all_entries:
                for entry in all_entries:
                    f.write(entry)
                print(f"🎉 Playlist Updated! Matches: {cricket_count}")
            else:
                print("⚠️ No cricket matches found.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
