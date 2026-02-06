import asyncio
import os
from playwright.async_api import async_playwright

async def run_packet_sniffer():
    async with async_playwright() as p:
        # Browser session storage
        user_data_dir = "./browser_session"
        
        # 1. Launch Lite Browser (Persistent but clean)
        # Hum caching use kar rahe hain isliye ye 'Lite' hi rahega
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # 2. EVERY PACKET SNIFFER (Exactly like HTTP Toolkit)
        found_link = None
        async def handle_request(request):
            nonlocal found_link
            # Amazon IVS pattern dhoondna (Screenshot 156691 success logic)
            if "playback.live-video.net" in request.url and ".m3u8" in request.url:
                found_link = request.url
                print(f"🎯 PACKET CAPTURED: {found_link}")

        # Toolkit style listener start
        page.on("request", handle_request)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Universal Packet Sniffing: {url}")

        try:
            # 3. Aggressive Loading (Mirroring Heavy Script success)
            # 60s timeout taaki heavy scripts ko load hone ka poora mauka mile
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # TRIGGER: Player ko click karna zaroori hai (Screenshot 156796)
            print("🖱️ Simulating user interaction...")
            await page.mouse.click(100, 100) 
            await asyncio.sleep(5)
            await page.mouse.click(250, 250) 
            
            # Final Wait: Wahi 47s window jo heavy script ko chahiye tha
            print("⏳ Scanning background traffic (40s)...")
            await asyncio.sleep(40)

            if found_link:
                print(f"✅ SUCCESS! SAVING LINK: {found_link}")
                with open("live_link.txt", "w") as f:
                    f.write(found_link)
            else:
                # Fallback: Agar splash screen par atka hai (Screenshot 1770367960149)
                print("❌ Packet nahi mila. Splash screen check...")
                status = await page.evaluate("() => document.title")
                print(f"💡 Page Title: {status}")

        except Exception as e:
            print(f"💥 Sniffer Error: {e}")

        await context.close()

if __name__ == "__main__":
    asyncio.run(run_packet_sniffer())
