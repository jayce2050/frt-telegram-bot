# bot_openai_env.py (giới hạn câu trả lời và chặn tin nhắn riêng)
import json
import openai
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatType
from telegram import Message
from typing import Optional

# Load biến môi trường từ file .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME")  # không có dấu @
openai.api_key = OPENAI_API_KEY

# Load dữ liệu từ detail.json
with open("A_crawl/detail.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Biến toàn cục để xử lý debounce
latest_message: Optional[Message] = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Hãy gắn thẻ tôi trong nhóm để được hỗ trợ kỹ thuật. Bot không phản hồi tin nhắn riêng.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global latest_message

    if not update.message or not update.message.text:
        return

    msg = update.message
    text = msg.text
    chat_type = msg.chat.type

    # ❌ Không phản hồi tin nhắn riêng
    if chat_type == ChatType.PRIVATE:
        return

    is_mentioned = BOT_USERNAME and f"@{BOT_USERNAME.lower()}" in text.lower()
    if not is_mentioned:
        return

    latest_message = msg
    current_message = msg

    # Chờ 7 giây để kiểm tra debounce
    await asyncio.sleep(7)
    if latest_message != current_message:
        return

    # Làm sạch truy vấn
    query = text.replace(f"@{BOT_USERNAME}", "").strip().lower()

    # Tìm kiếm thông minh: lọc bài viết có từ khóa gần giống
    keywords = query.split()
    scored_articles = []
    for article in articles:
        score = sum(1 for word in keywords if word in (article["title"] + article["content"]).lower())
        if score > 0:
            scored_articles.append((score, article))

    scored_articles.sort(reverse=True, key=lambda x: x[0])
    top_articles = [a for _, a in scored_articles[:5]]  # lấy tối đa 5 bài liên quan nhất

    context_text = "\n\n".join(
        [f"Tiêu đề: {a['title']}\nNội dung: {a['content'][:1500]}\nLink: {a.get('link', 'Không có')}" for a in top_articles]
    )

    has_match = len(scored_articles) > 0

    if has_match:
        prompt = f"""
Bạn là một trợ lý kỹ thuật nội bộ. Dựa trên các tài liệu sau, hãy trả lời chi tiết và có dẫn link cụ thể nếu có, cho câu hỏi: \"{query}\".

Tài liệu:
{context_text}

Nếu không đủ thông tin, hãy trả lời như sau:
\"Rất tiếc, hiện tại tôi chưa có câu trả lời chính xác cho vấn đề này. Bạn có thể thử kiểm tra lại một số cài đặt cơ bản hoặc thử khởi động lại thiết bị. Nếu vấn đề vẫn xảy ra, vui lòng liên hệ quản trị viên để được hỗ trợ thêm.\"

Hãy đảm bảo câu trả lời cụ thể, rõ ràng, có ví dụ nếu cần, có link nếu có.
"""
    else:
        prompt = f"""
Bạn là một trợ lý kỹ thuật nội bộ. Câu hỏi của người dùng là: \"{query}\"

Hiện tại, bạn không tìm thấy dữ liệu nội bộ phù hợp.
Hãy tìm kiếm trên Internet (như Google, diễn đàn kỹ thuật, tài liệu hỗ trợ...) để đưa ra một phương án trả lời ngắn gọn, đúng trọng tâm và hữu ích.

Sau đó, hãy phản hồi theo cấu trúc:
\"Rất tiếc, hiện tôi chưa có câu trả lời chính xác cho vấn đề này trong tài liệu nội bộ. Tuy nhiên bạn có thể tham khảo cách sau: [...phương án tìm được...]. Nếu vẫn không được, vui lòng liên hệ quản trị viên để được hỗ trợ.\"

Không cần ghi rõ nguồn hoặc liệt kê link web, chỉ cần nêu giải pháp gợi ý phù hợp.
**Không được khuyên người dùng liên hệ với trung tâm bảo hành, nhà sản xuất hoặc bên thứ ba.**
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Bạn là trợ lý kỹ thuật hỗ trợ người dùng nội bộ. Trả lời dựa vào tài liệu, nếu không có thì đưa ra gợi ý từ Internet. Không được khuyên người dùng liên hệ hãng hoặc bảo hành mà chỉ được nói 'liên hệ quản trị viên'."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )
        reply_text = response.choices[0].message["content"].strip()
        await update.message.reply_text(reply_text)
    except Exception as e:
        print(f"⚠️ Lỗi OpenAI: {e}")
        await update.message.reply_text("⚠️ Bot gặp lỗi khi xử lý câu hỏi.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE),
        search
    ))

    print("🚀 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
