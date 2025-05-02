# A_crawl/crawl_detail.py
import asyncio
import json
from playwright.async_api import async_playwright

INPUT_FILE = "A_crawl/list.json"
OUTPUT_FILE = "A_crawl/detail.json"
COOKIE_FILE = "A_crawl/cookies.json"

async def main():
    # Đọc danh sách link bài viết
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    result = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Nạp cookie từ trình duyệt thật
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            raw_cookies = json.load(f)

        cookies = []
        for c in raw_cookies:
            cookies.append({
                "name": c["Name raw"],
                "value": c["Content raw"],
                "domain": "tailieu.frt.vn",
                "path": c.get("Path raw", "/"),
                "expires": -1,
                "httpOnly": c.get("HTTP only raw", False) == "true",
                "secure": c.get("Send for raw", False) == "true",
                "sameSite": "Lax"
            })

        await context.add_cookies(cookies)

        for idx, article in enumerate(articles, 1):
            url = article["url"]
            title = article["title"]
            print(f"🔎 ({idx}/{len(articles)}) Đang xử lý: {title}")

            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("div#content", timeout=15000)

                # Trích nội dung
                content_element = await page.query_selector("div#content")
                content = await content_element.inner_text() if content_element else ""

                result.append({
                    "title": title,
                    "url": url,
                    "content": content.strip()
                })
            except Exception as e:
                print(f"⚠️ Lỗi khi xử lý {url}: {e}")

        # Ghi kết quả ra file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ Đã lưu nội dung {len(result)} bài viết vào {OUTPUT_FILE}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())