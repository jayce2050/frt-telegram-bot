# login.py
import asyncio
from playwright.async_api import async_playwright

# Thư mục lưu profile (cookie, cache, session…)
USER_DATA_DIR = "A_crawl/login_data"
LOGIN_URL = "https://tailieu.frt.vn"

async def main():
    async with async_playwright() as p:
        # Mở Chromium với profile lưu trữ
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False  # hiển thị cửa sổ để bạn tự login
        )
        page = await browser.new_page()
        await page.goto(LOGIN_URL)
        print("👉 Vui lòng đăng nhập thủ công trong cửa sổ này.")
        # Đợi 60s để bạn hoàn tất đăng nhập
        await page.wait_for_timeout(60000)
        await browser.close()
        print("✅ Đã lưu session vào", USER_DATA_DIR)

if __name__ == "__main__":
    asyncio.run(main())
