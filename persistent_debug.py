import asyncio
import os
from playwright.async_api import async_playwright

async def run_lite():
    async with async_playwright() as p:
        # Browser session folder (GitHub ise cache karega)
        user_data_dir = "./browser_session"
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # Lite Browser launch (Persistent mode)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()

        # Toolkit Style Listener: Network traffic monitor
        found_link = None
        async def capture_traffic(request):
            nonlocal found_link
            # Looking for playback.live-video.net (as seen in Toolkit)
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_link = request.url

        page.on("request", capture_traffic)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Fast-Scanning with Persistent Browser: {url}")

        try:
            # Fast Load: Sirf DOM tak ka wait
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Click to trigger link generation
            await page.mouse.click(5, 5)
            await asyncio.sleep(7) # Toolkit ko capture karne ka time de rahe hain

            if found_link:
                print(f"\n✅ SUCCESS! LINK CAPTURED: {found_link}")
                with open("live_link.txt", "w") as f:
                    f.write(found_link)
            else:
                print("\n❌ Link nahi mila. Match shayad offline hai.")

        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_lite())

