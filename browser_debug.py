import asyncio
from playwright.async_api import async_playwright

async def run_simulation():
    async with async_playwright() as p:
        # 1. Real Browser launch karo
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()

        url = "https://allrounderlive.pages.dev/dilz?id=65656576"
        print(f"📡 Launching Browser and loading: {url}")

        # 2. Page par jao aur JS load hone do
        await page.goto(url, wait_until="networkidle")
        
        # 3. Memory me 'playback_url' ya AWS link dhoondho
        # Hum wahi variable dhoond rahe hain jo App JSON me hai
        print("🕵️ Extracting dynamic variables from memory...")
        
        extracted_data = await page.evaluate("""() => {
            // Memory me playback_url check karo
            if (typeof playback_url !== 'undefined') return playback_url;
            
            // Agar variable nahi mila, to pure page ke scripts me pattern dhoondho
            const scripts = document.getElementsByTagName('script');
            for (let s of scripts) {
                if (s.innerHTML.includes('playback.live-video.net')) return 'FOUND_IN_SCRIPT';
            }
            return 'NOT_IN_MEMORY';
        }""")

        print(f"✅ BROWSER RESULT: {extracted_data}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_simulation())
