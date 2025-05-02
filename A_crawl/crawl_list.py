import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="auth.json")
        page = await context.new_page()

        await page.goto("https://tailieu.frt.vn/display/FSHOPKTHO")
        await page.wait_for_selector("div.results-container")

        print("✅ Đã mở trang, bắt đầu thu thập…")

        previous_count = 0
        max_try = 10
        try_count = 0

        while True:
            # Đếm số link hợp lệ hiện tại
            valid_links = await page.query_selector_all("div.results-container a[href*='/viewpage.action']")
            count = len(valid_links)
            print(f"🔎 Bài viết hiện tại: {count}")

            # Kiểm tra nếu không tăng số lượng nữa
            if count <= previous_count:
                try_count += 1
                if try_count >= max_try:
                    print("🛑 Không còn tăng số bài viết sau nhiều lần thử.")
                    break
            else:
                try_count = 0  # reset nếu có bài mới
                previous_count = count

            # Tìm nút Show more (đúng class="more-link")
            try:
                show_more = await page.query_selector("a.more-link")
                if not show_more:
                    print("✅ Không còn nút Show more.")
                    break
                await show_more.scroll_into_view_if_needed()
                await show_more.click()
                print("🔁 Đã click Show more, đợi 3s...")
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"⚠️ Lỗi khi click Show more: {e}")
                break

        # Lấy lại toàn bộ link bài viết hợp lệ
        final_links = []
        all_links = await page.query_selector_all("div.results-container a[href*='/viewpage.action']")
        for link in all_links:
            href = await link.get_attribute("href")
            title = await link.inner_text()
            if href and "CommentId" not in href:
                final_links.append({
                    "title": title.strip(),
                    "url": f"https://tailieu.frt.vn{href}" if href.startswith("/") else href
                })

        with open("A_crawl/list.json", "w", encoding="utf-8") as f:
            json.dump(final_links, f, ensure_ascii=False, indent=2)

        print(f"📦 Đã lưu tổng cộng {len(final_links)} bài viết vào A_crawl/list.json")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())