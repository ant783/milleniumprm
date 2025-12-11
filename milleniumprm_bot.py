from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Команда старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-повторяшка. Напиши что-нибудь, и я повторю!")

# Повторение сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(text)

if __name__ == '__main__':
    # Создаём приложение с токеном
    app = ApplicationBuilder().token("8275812174:AAHGIrL3Uw8AN7TKdNAtUZYFTi0lQu1Ni-A").build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запуск
    app.run_polling()
