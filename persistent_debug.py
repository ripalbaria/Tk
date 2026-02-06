import asyncio
from playwright.async_api import async_playwright

async def run_persistent_success():
    async with async_playwright() as p:
        # 1. Use Persistent Context for Lite behavior
        user_data_dir = "./browser_session"
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 2. Toolkit/Heavy Style Listener
        found_link = None
        async def catch_link(request):
            nonlocal found_link
            if "playback.live-video.net" in request.url:
                found_link = request.url

        page.on("request", catch_link)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Universal Scanning: {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 🔥 CRUCIAL STEP: Heavy script yahi click use karti hai (Screenshot 156796 logic)
            print("🖱️ Simulating user interaction (Clicking to trigger stream)...")
            await page.mouse.click(100, 100) 
            
            # Wait for the network to fire (Toolkit style)
            await asyncio.sleep(15) 

            if found_link:
                print(f"✅ SUCCESS! TOOLKIT LINK CAPTURED: {found_link}")
            else:
                print("❌ Link nahi mila traffic me.")
        except Exception as e:
            print(f"💥 Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_persistent_success())
