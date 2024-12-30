import nest_asyncio
import asyncio
import signal

from globals                 import BOT_TOKEN
from lib.bot_buttom_handler  import button_handler
from lib.bot_session_manager import clean_up_sessions
from lib.bot_commands        import *
from telegram                import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup
from telegram.ext            import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, CallbackContext

nest_asyncio.apply()

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Список доступных команд"),
        BotCommand("irregular_verbs", "Изучить неправильные глаголы"),
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CallbackQueryHandler(button_handler))

    cleanup_task = asyncio.create_task(clean_up_sessions())

    def shutdown_signal_handler(sig, frame):
        print("Получен сигнал завершения. Завершаем работу...")
        asyncio.create_task(shutdown(app, cleanup_task))

    signal.signal(signal.SIGINT, shutdown_signal_handler)
    signal.signal(signal.SIGTERM, shutdown_signal_handler)

    print("Бот запущен!")
    app.run_polling()

async def shutdown(app, cleanup_task):
    cleanup_task.cancel()
    await app.stop()
    print("Бот остановлен.")
    asyncio.get_event_loop().stop()

if __name__ == "__main__":
    asyncio.run(main())