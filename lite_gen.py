import asyncio
from playwright.async_api import async_playwright

async def run_ultra_lite():
    async with async_playwright() as p:
        # Lite mode browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        found_link = None
        async def sniff(request):
            nonlocal found_link
            # Toolkit/PCAPdroid pattern detection
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_link = request.url

        page.on("request", sniff)
        
        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Ultra-Lite Scanning: {url}")

        try:
            # 1. Page load (No clicks needed based on PCAPdroid)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # 2. Sirf 10 seconds wait (Resources bachane ke liye)
            await asyncio.sleep(10) 

            if found_link:
                print(f"✅ SUCCESS: {found_link}")
                with open("live_link.txt", "w") as f: f.write(found_link)
            else:
                print("❌ Link nahi mila (Time badhana pad sakta hai).")
        except Exception as e:
            print(f"💥 Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ultra_lite())

