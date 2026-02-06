import asyncio
import os
from playwright.async_api import async_playwright

async def run_persistent_success():
    async with async_playwright() as p:
        # Browser cache storage setup
        user_data_dir = "./browser_session"
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # Launching Persistent Context (Mirroring Heavy Script Logic)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # SUCCESS LOGIC: EXACT same listener used in 'simulate_browser' (156796.jpg)
        found_aws_link = None
        async def on_request(request):
            nonlocal found_aws_link
            # Toolkit style pattern from your success screenshot
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_aws_link = request.url

        page.on("request", on_request)

        # Target Channel ID
        target_id = "65656576"
        url = f"https://allrounderlive.pages.dev/dilz?id={target_id}"
        print(f"📡 Mirror Scanning: {url}")

        try:
            # 1. Wait until network is fully IDLE (Heavy script strategy)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 2. TRIGGER interaction exactly like 156796.jpg
            print("🖱️ Simulating Success Interaction (Clicking stream)...")
            await page.mouse.click(100, 100)
            
            # 3. PATIENCE: Wait for the EXACT same duration that worked (45-50s)
            print("⏳ Waiting for background traffic capture (30s)...")
            await asyncio.sleep(30)

            if found_aws_link:
                print(f"✅ SUCCESS! TOOLKIT LINK CAPTURED: {found_aws_link}")
                # Write to file for playlist update
                with open("live_link.txt", "w") as f:
                    f.write(found_aws_link)
            else:
                # Fallback: Print what browser actually sees
                print("❌ Link nahi mila traffic me.")
                title = await page.title()
                print(f"💡 Page Status: {title}")

        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_persistent_success())
