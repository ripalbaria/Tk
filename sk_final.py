import requests
import base64
import json
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
        # 1. Custom Mapping
        mapped = "".join([LOOKUP_TABLE[ord(c)] if ord(c) < len(LOOKUP_TABLE) else c for c in encrypted_text])
        # 2. B64 Decode & Reverse
        decoded_str = base64.b64decode(mapped).decode('utf-8')[::-1]
        # 3. Second B64 & AES
        ciphertext = base64.b64decode(decoded_str)
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')
    except Exception:
        return None

def fetch_match_streams(event_data):
    """
    Fetches the specific stream file using the 'links' path (e.g., pro/xyz.txt)
    """
    entries = []
    
    # Extract Info
    title = event_data.get('eventName', 'Cricket Match')
    team_a = event_data.get('teamAName', '')
    team_b = event_data.get('teamBName', '')
    if team_a and team_b:
        title = f"{team_a} vs {team_b} - {event_data.get('eventName', '')}"
        
    logo = event_data.get('eventLogo', '')
    
    # KEY FIX: Use the explicit 'links' path found in JSON
    # Example: "pro/SUNDIF...txt"
    link_path = event_data.get('links')
    
    if not link_path:
        return []

    full_url = f"{BASE_URL}/{link_path}"
    print(f"   ⚡ Fetching streams from: {link_path}")
    
    try:
        res = requests.get(full_url, headers=HEADERS, timeout=10)
        if res.status_code != 200:
            return []
            
        decrypted_streams = decrypt_sk_tech(res.text)
        if not decrypted_streams:
            return []

        # Parse the Stream File (It's usually a JSON list of objects)
        try:
            stream_list = json.loads(decrypted_streams)
            
            # Helper to handle different formats (List vs Dict)
            if isinstance(stream_list, dict): 
                stream_list = stream_list.get('streamUrls', [])
            
            if isinstance(stream_list, list):
                for idx, item in enumerate(stream_list):
                    # Sometimes item is a dict, sometimes just a string url
                    if isinstance(item, dict):
                        stream_url = item.get('link') or item.get('url')
                        stream_name = item.get('title') or item.get('name') or f"Link {idx+1}"
                        
                        # Check DRM
                        drm_scheme = item.get('drmScheme')
                        drm_license = item.get('drmLicense')
                    else:
                        stream_url = str(item)
                        stream_name = f"Link {idx+1}"
                        drm_scheme = None

                    if stream_url:
                        # Construct M3U Entry
                        entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="Cricket", {title} ({stream_name})\n'
                        
                        # Add headers or DRM info if present
                        if drm_scheme and drm_license:
                            entry += f'#KODIPROP:inputstream.adaptive.license_type={drm_scheme}\n'
                            entry += f'#KODIPROP:inputstream.adaptive.license_key={drm_license}\n'
                        
                        entry += f'#EXTVLCOPT:http-user-agent={HEADERS["User-Agent"]}\n'
                        entry += f'{stream_url}\n'
                        entries.append(entry)
                        
        except json.JSONDecodeError:
            # Fallback if it's just raw text lines
            print("      ⚠️ Warning: Stream file was not JSON. Using raw text.")
            if "http" in decrypted_streams:
                entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="Cricket", {title}\n{decrypted_streams.strip()}\n'
                entries.append(entry)

    except Exception as e:
        print(f"      ❌ Error fetching stream details: {e}")

    return entries

def main():
    print("🚀 Starting SK Live Cricket Scraper...")
    all_entries = []
    
    try:
        # 1. Fetch Main Events
        res = requests.get(f"{BASE_URL}/events.txt", headers=HEADERS, timeout=15)
        raw_data = decrypt_sk_tech(res.text)
        
        if not raw_data:
            print("❌ Failed to decrypt main events list.")
            return

        # 2. Parse Outer List
        # The file is a list of wrappers: [{"event": "{...}"}, {"event": "{...}"}]
        wrapper_list = json.loads(raw_data)
        print(f"📋 Found {len(wrapper_list)} total events.")
        
        for wrapper in wrapper_list:
            # 3. Parse Inner JSON string
            event_str = wrapper.get('event')
            if not event_str: continue
            
            try:
                event = json.loads(event_str)
                
                # 4. Filter for CRICKET
                cat = event.get('category', '').strip().lower()
                name = event.get('eventName', '').strip().lower()
                
                # Check for "cricket" (case insensitive)
                if 'cricket' in cat or 'cricket' in name:
                    print(f"🏏 Found Match: {event.get('eventName')}")
                    match_entries = fetch_match_streams(event)
                    all_entries.extend(match_entries)
                    
            except json.JSONDecodeError:
                continue

        # 5. Write Playlist
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            if all_entries:
                for entry in all_entries:
                    f.write(entry)
                print(f"🎉 Success! Saved {len(all_entries)} streams to playlist.m3u")
            else:
                print("⚠️ No active cricket streams found right now.")

    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()
