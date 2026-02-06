from playwright.sync_api import sync_playwright

URL = "https://allrounderlive.pages.dev/dilz?id=65656576"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    found = None

    def handle_request(req):
        nonlocal found
        u = req.url

        if ".m3u8" in u or "playback.live-video.net" in u:
            found = u

    page.on("request", handle_request)

    page.goto(URL, wait_until="networkidle")

    browser.close()

    if found:
        print(found)
        open("link.txt", "w").write(found)
    else:
        print("Not found")
