import requests
import base64
import json
import os
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- CONFIGURATION ---
# We use the SK Tech Key/IV hardcoded here since we know them from previous steps.
# You can also use os.environ.get() if you prefer secrets.
BASE_URL = "https://sufyanpromax.space" # Base URL of the API
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"

# Headers to mimic the app
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Connection": "keep-alive"
}

# The Custom Lookup Table (extracted from SK Tech)
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
    """
    The specific 5-step decryption logic for SK Tech
    """
    if not encrypted_text: return None
    try:
        # 1. Custom Character Mapping
        mapped = []
        for c in encrypted_text:
            val = ord(c)
            if val < len(LOOKUP_TABLE):
                mapped.append(LOOKUP_TABLE[val])
            else:
                mapped.append(c)
        mapped_str = "".join(mapped)

        # 2. Base64 Decode -> UTF-8 String
        decoded_bytes = base64.b64decode(mapped_str)
        decoded_str = decoded_bytes.decode('utf-8')

        # 3. REVERSE the string
        reversed_str = decoded_str[::-1]

        # 4. Base64 Decode again -> Ciphertext bytes
        ciphertext = base64.b64decode(reversed_str)

        # 5. AES Decryption
        cipher = AES.new(KEY, AES.MODE_CBC, IV)
        decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted_bytes.decode('utf-8')

    except Exception as e:
        # print(f"Decryption failed: {e}") # Uncomment for debugging
        return None

def get_match_links(event):
    """
    Fetches details using the 'slug' if direct URL is missing or internal.
    """
    links_found = []
    
    # Extract basic info
    title = event.get('title', 'Live Match')
    logo = event.get('logo', '') or event.get('icon', '')
    
    # Priority 1: Check if 'url' is already a playable link
    direct_url = event.get('url', '')
    if direct_url and "http" in direct_url and ".txt" not in direct_url:
        # It's a direct link, add it immediately
        entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="Cricket", {title}\n'
        entry += f'{direct_url}\n'
        links_found.append(entry)
        return links_found

    # Priority 2: Use Slug to find the file
    slug = event.get('slug')
    
    # If no slug, maybe the 'url' points to a text file?
    if not slug and direct_url and ".txt" in direct_url:
        slug = direct_url # Treat the text URL as the target
    
    if not slug: 
        return []

    print(f"🔎 Scanning details for: {title} ({slug})")
    
    # Construct potential URLs for the detail file
    # Note: Adjust logic if the app uses a different path structure
    potential_urls = []
    if "http" in slug:
        potential_urls.append(slug)
    else:
        potential_urls.append(f"{BASE_URL}/channels/{slug}.txt")
        potential_urls.append(f"{BASE_URL}/events/{slug}.txt")

    valid_response_text = None

    for url in potential_urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code == 200 and len(res.text) > 10:
                valid_response_text = res.text
                break
        except:
            continue

    if not valid_response_text:
        return []

    # Decrypt the detail file
    decrypted_detail = decrypt_sk_tech(valid_response_text)
    
    if decrypted_detail:
        try:
            # Handle if the result is a List or a Dict
            if decrypted_detail.startswith("["):
                streams = json.loads(decrypted_detail)
            else:
                # Sometimes it might just be a raw URL string
                streams = [{"link": decrypted_detail, "title": "Main Stream"}]

            # If it's a dict wrapper (like Cricfy)
            if isinstance(streams, dict):
                 streams = streams.get('streamUrls', [])

            for s in streams:
                if isinstance(s, str): continue # Skip junk
                
                stream_title = s.get('title', 'Link')
                stream_url = s.get('link') or s.get('url')
                
                if stream_url:
                    entry = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{title}", {stream_title}\n'
                    # Add headers for players if needed
                    if "m3u8" in stream_url:
                        entry += f'#EXTVLCOPT:http-user-agent={HEADERS["User-Agent"]}\n'
                    entry += f'{stream_url}\n'
                    links_found.append(entry)
        except Exception as e:
            print(f"Error parsing details: {e}")

    return links_found

def main():
    print("🚀 Connecting to SK Tech Server...")
    all_entries = []
    
    # 1. Fetch Main List
    try:
        # Update this URL to the main list location
        MAIN_LIST_URL = f"{BASE_URL}/events.txt" 
        response = requests.get(MAIN_LIST_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        # 2. Decrypt Main List
        decrypted_json = decrypt_sk_tech(response.text)
        
        if not decrypted_json:
            print("❌ Failed to decrypt main list.")
            return
            
        events = json.loads(decrypted_json)
        print(f"📋 Found {len(events)} total events.")

        # 3. Filter and Process
        for event in events:
            # Check Title or Category for 'Cricket'
            title = event.get('title', '').lower()
            category = event.get('category', '').lower()
            
            is_cricket = "cricket" in title or "cricket" in category or "ipl" in title or "t20" in title
            
            if is_cricket:
                entries = get_match_links(event)
                all_entries.extend(entries)

        # 4. Save to Playlist
        with open("playlist.m3u", "w", encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for entry in all_entries:
                f.write(entry)
        
        print(f"🎉 Playlist Updated: {len(all_entries)} streams added.")
        
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    main()
