# save_auth.py
import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://tailieu.frt.vn/display/FSHOPKTHO")
        print("⏳ Vui lòng đăng nhập bằng tay trong cửa sổ vừa mở...")
        await page.wait_for_timeout(30000)  # 30 giây để bạn login tay
        await context.storage_state(path="auth.json")
        print("✅ Đã lưu file auth.json thành công.")
        await browser.close()

asyncio.run(run())
