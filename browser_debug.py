import asyncio
from playwright.async_api import async_playwright

async def run_simulation():
    async with async_playwright() as p:
        # 1. Real Chrome launch karo
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 2. Toolkit style: Network listener
        found_aws_links = []
        async def catch_network(request):
            if "playback.live-video.net" in request.url:
                found_aws_links.append(request.url)

        page.on("request", catch_network)

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Launching Browser Simulation: {url}")

        try:
            # 3. Page load karo
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 4. TRIGGER: Search and Click the Play button or Iframe
            # Aksar link tabhi trigger hota hai jab interaction ho
            print("🖱️ Simulating user interaction (Clicking to trigger stream)...")
            await page.mouse.click(100, 100) # Random click to trigger JS
            await asyncio.sleep(10) # Wait for background requests

            if found_aws_links:
                print("\n✅ SUCCESS! TOOLKIT LINK CAPTURED:")
                for link in set(found_aws_links):
                    print(f"🔗 {link}")
            else:
                print("\n❌ Network traffic me link nahi mila.")
                # Fallback: pure page ke HTML me bikhre hue pattern dhoondo
                content = await page.content()
                if "playback.live-video.net" in content:
                    print("💡 Link found in raw HTML after JS execution.")
                else:
                    print("😢 Link still hidden. Match might be officially offline.")

        except Exception as e:
            print(f"💥 Browser Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
