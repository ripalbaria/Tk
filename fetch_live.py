import requests
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Configuration
URL = "https://sufyanpromax.space/events.txt"
KEY = b"l2l5kB7xC5qP1rK1"
IV = b"p1K5nP7uB8hH1l19"
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

def decrypt_data(raw_text):
    # Step 1: Custom Map
    mapped = "".join([LOOKUP_TABLE[ord(c)] if ord(c) < len(LOOKUP_TABLE) else c for c in raw_text])
    # Step 2: B64 Decode & Reverse
    decoded_str = base64.b64decode(mapped).decode('utf-8')[::-1]
    # Step 3: Second B64 & AES
    ciphertext = base64.b64decode(decoded_str)
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode('utf-8')

def main():
    response = requests.get(URL)
    decrypted_json = decrypt_data(response.text)
    data = json.loads(decrypted_json)
    
    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n")
        # Adjust 'category' or 'title' keys based on the actual JSON structure
        for item in data:
            if "cricket" in item.get("category", "").lower() or "cricket" in item.get("title", "").lower():
                f.write(f"#EXTINF:-1,{item.get('title', 'Live Event')}\n")
                f.write(f"{item.get('url')}\n")

if __name__ == "__main__":
    main()

