import asyncio
import os
from playwright.async_api import async_playwright

async def run_universal_extractor():
    async with async_playwright() as p:
        # 1. Persistent Data (Lite Browser Storage)
        user_data_dir = "./browser_session"
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # Launching the Lite Chromium Browser
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()

        # 2. Network Sniffer (Wahi jo Toolkit me success hua tha)
        found_link = None
        async def sniff_traffic(request):
            nonlocal found_link
            # Har wo link jo playback.live-video.net se hai aur m3u8 hai
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_link = request.url

        page.on("request", sniff_traffic)

        # Universal ID Input (Aap isse cric_gen.py se pass karenge)
        target_id = "65656576" 
        url = f"https://allrounderlive.pages.dev/dilz?id={target_id}"
        print(f"📡 Universal Scanning: {url}")

        try:
            # 3. Execution Logic
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            
            # Link trigger karne ke liye "Blind Clicks" (Interaction Simulation)
            # Bina iske JS stream trigger nahi karta
            await page.mouse.click(10, 10) 
            await asyncio.sleep(2)
            await page.mouse.click(100, 100) 

            # Capture ke liye wait (Toolkit style)
            await asyncio.sleep(12) 

            if found_link:
                print(f"✅ SUCCESS! FOUND LINK: {found_link}")
                with open("live_link.txt", "w") as f: f.write(found_link)
            else:
                print("❌ Link nahi mila traffic me.")
                
        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_universal_extractor())
