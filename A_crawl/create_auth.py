from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://tailieu.frt.vn")
    print("👉 Vui lòng đăng nhập thủ công rồi nhấn Enter trong terminal khi xong.")
    input()
    context.storage_state(path="auth.json")
    print("✅ Đã lưu session vào auth.json")
    browser.close()
