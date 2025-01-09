import nest_asyncio
import asyncio

from globals                 import BOT_TOKEN
from lib.bot_buttom_handler  import button_handler
from lib.bot_session_manager import clean_up_sessions
from lib.bot_commands        import *
from telegram                import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup
from telegram.ext            import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, CallbackContext, PollAnswerHandler

nest_asyncio.apply()

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом")
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CallbackQueryHandler(button_handler))

    cleanup_task = asyncio.create_task(clean_up_sessions())

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())