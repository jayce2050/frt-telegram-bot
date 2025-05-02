# open_browser_manual.py
import asyncio
from playwright.async_api import async_playwright

LOGIN_DATA_DIR = "A_crawl/login_data"

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch_persistent_context(
            user_data_dir=LOGIN_DATA_DIR,
            headless=False
        )
        page = await browser.new_page()
        await page.goto("https://tailieu.frt.vn/display/FSHOPKTHO")
        print("🧠 Đăng nhập tay vào trình duyệt vừa mở. Sau khi xong, hãy ĐÓNG TRÌNH DUYỆT rồi chạy lại crawl_detail.py")
        await page.wait_for_timeout(300000)  # 5 phút cho bạn đăng nhập
        await browser.close()

asyncio.run(main())