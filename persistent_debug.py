import asyncio
import os
from playwright.async_api import async_playwright

async def run_persistent_final():
    async with async_playwright() as p:
        # Browser session storage
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

        # 2. Advanced Traffic Sniffer (Toolkit Style)
        found_aws_link = None
        async def sniff(request):
            nonlocal found_aws_link
            # Catching the exact pattern from your success run
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_aws_link = request.url

        page.on("request", sniff)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Universal Scanning: {url}")

        try:
            # 3. Wait for full network idle (Heavy script logic)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 🔥 MULTI-CLICK TRIGGER: Alag-alag jagah click karke player force karein
            print("🖱️ Simulating aggressive user interaction...")
            coords = [(100, 100), (300, 300), (50, 50)]
            for x, y in coords:
                await page.mouse.click(x, y)
                await asyncio.sleep(1)

            # ⏳ WAIT TIME: Success run 47s chala tha, hum bhi wahi karenge
            print("⏳ Final wait for dynamic token (30s)...")
            await asyncio.sleep(30) 

            if found_aws_link:
                print(f"✅ SUCCESS! LINK CAPTURED: {found_aws_link}")
                # Save it permanently
                with open("live_link.txt", "w") as f:
                    f.write(found_aws_link)
            else:
                print("❌ Link nahi mila. Trying fallback source scan...")
                # Backup: Check if link is in page source
                content = await page.content()
                if "playback.live-video.net" in content:
                    print("💡 Link found in raw HTML source!")
                else:
                    print("😢 Stream not triggered. Match might be offline.")

        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_persistent_final())
