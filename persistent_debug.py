import asyncio
import os
from playwright.async_api import async_playwright

async def run_packet_sniffer():
    async with async_playwright() as p:
        # 1. Fresh Browser launch (No session persistence to avoid splash trap)
        # Lekin GitHub cache browser files (110MB) ko save rakhega
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        
        # Fresh context for every run
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # 2. EVERY PACKET SNIFFER (Toolkit Style)
        found_link = None
        async def handle_request(request):
            nonlocal found_link
            # Amazon IVS pattern search (Screenshot 156691 success logic)
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_link = request.url
                print(f"🎯 PACKET CAPTURED: {found_link}")

        page.on("request", handle_request)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Universal Packet Sniffing: {url}")

        try:
            # 3. Mirror Heavy Script's timing (47s to 60s)
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # TRIGGER interaction (Screenshot 156796 success)
            print("🖱️ Simulating Success Interaction...")
            await page.mouse.click(100, 100) 
            await asyncio.sleep(5)
            await page.mouse.click(300, 300) 
            
            # Final Scanning Window
            print("⏳ Scanning background traffic (40s)...")
            await asyncio.sleep(40)

            if found_link:
                print(f"✅ SUCCESS! SAVING LINK: {found_link}")
                with open("live_link.txt", "w") as f: f.write(found_link)
            else:
                print("❌ Packet nahi mila. Splash screen pe atka hai.")
                # Debug info
                print(f"💡 Final Page Title: {await page.title()}")

        except Exception as e:
            print(f"💥 Sniffer Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_packet_sniffer())
