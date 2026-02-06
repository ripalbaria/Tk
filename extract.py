import re
from playwright.sync_api import sync_playwright

URL = "https://run-machine.pages.dev/?id=hindi"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle")

    html = page.content()

    match = re.search(r'https?://[^"\']+\.m3u8[^"\']*', html)

    if match:
        open("link.txt", "w").write(match.group(0))
        print(match.group(0))
    else:
        print("Not found")

    browser.close()
