import asyncio
import os
from playwright.async_api import async_playwright

async def run_persistent_success():
    async with async_playwright() as p:
        # Browser session data (GitHub cache ise handle karega)
        user_data_dir = "./browser_session"
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # 1. Launch Persistent Context (Lite but Smart)
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 2. Toolkit Style Listener (Capture Link from Traffic)
        found_aws_link = None
        async def capture_traffic(request):
            nonlocal found_aws_link
            # Looking for the exact AWS IVS pattern found in successful run
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_aws_link = request.url

        page.on("request", capture_traffic)

        target_url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Universal Scanning: {target_url}")

        try:
            # 3. Increase Timeout and Interaction (Copying Heavy Script)
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            
            print("🖱️ Simulating user interaction (Clicking to trigger stream)...")
            # Multiple clicks alag-alag coordinates par taaki player trigger ho jaye
            await page.mouse.click(100, 100)
            await asyncio.sleep(2)
            await page.mouse.click(250, 250)
            
            # 🔥 CRUCIAL: Wait more time like the heavy script (47s total)
            print("⏳ Waiting for dynamic token generation...")
            await asyncio.sleep(25) 

            if found_aws_link:
                print(f"✅ SUCCESS! TOOLKIT LINK CAPTURED: {found_aws_link}")
                with open("live_link.txt", "w") as f:
                    f.write(found_aws_link)
            else:
                print("❌ Link nahi mila traffic me. Try increasing wait time.")

        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_persistent_success())
