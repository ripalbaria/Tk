from playwright.sync_api import sync_playwright

URL = "https://allrounderlive.pages.dev/dilz?id=65656576"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    found = [None]

    def handle_request(req):
        u = req.url
        if "playback.live-video.net" in u or ".m3u8" in u:
            found[0] = u

    page.on("request", handle_request)

    page.goto(URL)

    # ✅ wait page load
    page.wait_for_timeout(5000)

    # ✅ simulate user interaction
    page.mouse.click(400, 400)

    # ✅ wait for stream fetch
    page.wait_for_timeout(8000)

    browser.close()

    if found[0]:
        print(found[0])
        open("link.txt", "w").write(found[0])
    else:
        print("Not found")
