# A_crawl/


import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INPUT_FILE = "A_crawl/list.json"
OUTPUT_FILE = "A_crawl/detail.json"

# Đường dẫn đến thư mục profile Firefox thật của bạn
FIREFOX_PROFILE_PATH = "/Users/jayce/Library/Application Support/Firefox/Profiles/default-release"

def main():
    # Load danh sách bài viết
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        articles = json.load(f)

    # Cấu hình Firefox dùng profile thật
    options = Options()
    options.set_preference("profile", FIREFOX_PROFILE_PATH)
    options.set_preference("dom.webdriver.enabled", False)  # Ẩn chế độ selenium
    options.set_preference("useAutomationExtension", False)
    options.add_argument("--start-maximized")

    driver = webdriver.Firefox(options=options)

    results = []

    for idx, article in enumerate(articles, 1):
        title = article["title"]
        url = article["url"]
        print(f"🔎 ({idx}/{len(articles)}) Đang lấy: {title}")

        try:
            driver.get(url)
            # Đợi tối đa 20s để nội dung xuất hiện
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "content"))
            )

            content_element = driver.find_element(By.ID, "content")
            content = content_element.text.strip()

            results.append({
                "title": title,
                "url": url,
                "content": content
            })

        except Exception as e:
            print(f"⚠️ Lỗi ở {url}: {e}")
            continue

    # Ghi kết quả ra file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"✅ Đã lưu {len(results)} bài viết vào {OUTPUT_FILE}")
    driver.quit()

if __name__ == "__main__":
    main()
