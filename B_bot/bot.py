# bot.py
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ChatType

# Load dữ liệu từ detail.json
with open("A_crawl/detail.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

TOKEN = "7143633563:AAFDEAAk-IpXCQIvzT3Hzb8OsiX4nuIikXA"  # <-- Thay bằng token bạn lấy từ BotFather

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Bạn hãy nhập từ khóa để tìm bài viết nhé.")

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()
    results = []

    for article in articles:
        if query in article["title"].lower() or query in article["content"].lower():
            results.append(f"📄 {article['title']}\n🔗 {article['url']}")

    if results:
        reply = "\n\n".join(results[:5])  # trả về tối đa 5 bài đầu tiên
        await update.message.reply_text(reply)
    else:
        await update.message.reply_text("❌ Không tìm thấy bài viết nào phù hợp.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
    filters.TEXT & (filters.ChatType.GROUPS | filters.ChatType.PRIVATE), search
))

    print("🚀 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
