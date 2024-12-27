import aiofiles
import aiosqlite
import nest_asyncio
import asyncio
import io
import os
import time
import signal

from dotenv       import load_dotenv
from telegram     import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, CallbackContext
from datetime     import datetime, timedelta

## NEED FOR WORK asyncio IN PYCHARM
nest_asyncio.apply()

## Load data from .env
load_dotenv()


## START GLOBAL VARIABLES
BOT_TOKEN       = os.getenv("BOT_TOKEN")
DB_NAME         = os.getenv("DB_NAME")
IMAGE_PATH      = os.getenv("IMAGE_PATH")
VERBS_COUNT     = int(os.getenv("VERBS_COUNT"))
VERBS_WORK      = False
USER_SESSION    = {}
SESSION_TIMEOUT = timedelta(minutes=10)
image_cache     = {}
TTL             = 86400  # 24 часа

if not IMAGE_PATH:
    raise ValueError("Путь к файду не найден! Убедитесь, что файл .env существует и содержит IMAGE_PATH.")

if not DB_NAME:
    raise ValueError("Имя базы данных не найденно! Убедитесь, что файл .env существует и содержит DB_NAME.")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден! Убедитесь, что файл .env существует и содержит BOT_TOKEN.")
## END GLOBAL VARIABLES

## Function for help
# Put a bit on index -> void
def set_bit(progress, index):
    byte_index = index // 8
    bit_index  = index % 8
    progress[byte_index] |= (1 << bit_index)

# Check bit on index -> bool
def is_bit_set(progress, index):
    byte_index = index // 8
    bit_index  = index % 8
    return (progress[byte_index] & (1 << bit_index)) != 0

# Get first 5 not learned verb index -> int
def find_next_unlearned(progress, size):
    indexes = []
    for i in range(0, VERBS_COUNT):
        if not is_bit_set(progress, i):
            indexes.append(i + 1)
            if len(indexes) == size:
                break
    return indexes

# Start clock -> void
def start_user_session(user_id, verbs_indexes, mes_id):
    USER_SESSION[user_id] = {
        "verbs_id": verbs_indexes,
        "message_id": mes_id,
        "index": 0,
        "start_time": datetime.now()
    }

# Check active session -> time
def is_session_active(user_id):
    session = USER_SESSION.get(user_id)
    if not session:
        return False
    return datetime.now() - session["start_time"] < SESSION_TIMEOUT

# Delete time -> void
async def clear_expired_sessions():
    now = datetime.now()
    expired_users = [
        user_id for user_id, session in USER_SESSION.items()
        if now - session["start_time"] > SESSION_TIMEOUT
    ]
    for user_id in expired_users:
        del USER_SESSION[user_id]

# Time manager -> void
async def clean_up_sessions():
    while True:
        try:
            await clear_expired_sessions()
        except Exception as e:
            print(f"Ошибка в процессе очистки сессий: {e}")
        await asyncio.sleep(60 * 2)

#
def get_image(image_path):
    current_time = time.time()
    cached_image = image_cache.get(image_path)
    if cached_image and current_time - cached_image['timestamp'] < TTL:
        return cached_image['data']
    else:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        image_cache[image_path] = {'data': image_data, 'timestamp': current_time}
        return image_data
#
## END HELP FUNCTION

## START DATABASE SEGMENT
# add new user in sqlite db -> void
async def add_user_in_db(user_id, username):
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        row    = await cursor.fetchone()
        if not row :
            await conn.execute('''
                        INSERT INTO users (id, username, progress)
                        VALUES (?, ?, ?)
                    ''', (user_id, username, bytearray(VERBS_COUNT // 8)))
            await conn.commit()
            print(f"Добавлен новый пользователь в таблицу users: {user_id}, {username}")
        else:
            print(f"Пользователь: {username} уже есть в таблице users!")

# Update user progress -> void
async def upd_usr_progress(user_id, verbs_id):
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor       = await conn.execute("SELECT progress FROM users WHERE id = ?", (user_id,))
        row          = await cursor.fetchone()
        progress     = bytearray(row[0])

        for verb_index in verbs_id:
            set_bit(progress, verb_index - 1)

        await conn.execute("UPDATE users SET progress = ? WHERE id = ?", (progress, user_id))
        await conn.commit()
#
## END DATABASE SEGMENT


## SEARCH IRREGULAR VERBS
async def search_present_simple(verb):
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.execute("SELECT id, base_form FROM verbs")
        verbs  = await cursor.fetchall()

        for v in verbs:
            if v[1].startswith(verb):
                return v[0]
    return None 

async def search_past_simple(verb):
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.execute("SELECT id, past_simple FROM verbs")
        row  = await cursor.fetchall()

        for id, verbs in row:
            parts = verbs.split(" ") # parts[0] = verbs, parts[1] = transcriptions
            part  = parts[0].split("/")
            if part[0] == verb or (len(part) > 1 and part[1] == verb):
                return id
    return None

async def search_past_participle(verb):
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor = await conn.execute("SELECT id, past_participle FROM verbs")
        row = await cursor.fetchall()

        for id, verbs in row:
            parts = verbs.split(" ")  # parts[0] = verbs, parts[1] = transcriptions
            part = parts[0].split("/")
            if part[0] == verb or (len(part) > 1 and part[1] == verb):
                return id
    return None
## END SEARCH


## START BOT COMMAND SEGMENT
# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
             "Привет\\!\\ Я бот для помощи с изучением английского языка\\.\\ \n\n"
             "Ты можешь начать с команды /irregular\\_\\verbs, чтобы изучать неправильные глаголы\\.\\ \n"
             "Или используй команду /help, чтобы узнать что я умею\\.",  parse_mode='MarkdownV2'
    )

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я могу помочь тебе с твоим английским\\!\\:\\\n\n"
        "Системные команды\\:\\\n\n"
        "/start \\-\\ ознакомительный текст\n/help \\-\\ показать доступные команды\n\n"
        "Учёбные команды\\:\\\n\n"
        "/irregular\\_\\verbs \\-\\ учить неправильные глаголы\n\n"
        "Тесты\\:\\\n\n", parse_mode='MarkdownV2'
    )

# Command: /irregular_verbs
async def irregular_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_session_active(update.effective_user.id):
        await update.message.reply_text("Команда уже активна. Завершите текущую сессию, чтобы начать новую.")
        return

    try:
        user_id   = update.effective_user.id
        user_name = update.effective_user.username
        await add_user_in_db(user_id, user_name)

        async with aiosqlite.connect(DB_NAME) as conn:
            cursor   = await conn.execute("SELECT progress FROM users WHERE id = ?", (user_id,))
            row      = await cursor.fetchone()
            progress = bytearray(row[0])
            verbs_indexes  = find_next_unlearned(progress, 7)

            if len(verbs_indexes) == 0:
                await update.message.reply_text("Вы уже изучили все доступные глаголы!")
                return

        keyboard = [
            [
                InlineKeyboardButton("Приступить к выполнению", callback_data="ok"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.message.reply_text(
            "Вы готовы начать изучение следующего набора глаголов?",
            reply_markup=reply_markup
        )
        start_user_session(user_id, verbs_indexes, message.message_id)

    except aiosqlite.Error as db_error:
        await update.message.reply_text(f"Ошибка базы данных: {db_error}")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

async def echo(update: Update, context: CallbackContext):
    verb = update.message.text.lower()

    functions = [
        search_present_simple,
        search_past_simple,
        search_past_participle
    ]
    for function in functions:
        verb_id = await function(verb)
        if verb_id:
            image_path = IMAGE_PATH + str(verb_id) + '.png'
            try:
                img = get_image(image_path)
                await update.message.reply_photo(photo=img)
                return
            except Exception as e:
                await update.message.reply_text(f"Не удалось загрузить изображение: {e}")
                return

    await update.message.reply_text(f"Глагол {verb} не найден в базе данных.")

#
## END BOT COMMAND SEGMENT

## START BUTTON HANDLER SEGMENT
# Handler for button 'ok' -> void
async def button_ok(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict  = USER_SESSION.get(update.effective_user.id)
    verb_id   = user_dict.get("verbs_id")[0]
    prev_message_id = user_dict.get("message_id")


    keyboard = [
        [
            InlineKeyboardButton("Next", callback_data="next")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    image_path = IMAGE_PATH + str(verb_id) + '.png'
    img        = get_image(image_path)

    new_message = await update.callback_query.message.reply_photo(photo=img, reply_markup=reply_markup)

    if prev_message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
        except Exception as e:
            print(f"Не удалось удалить предыдущее сообщение: {e}")

    user_dict["message_id"] = new_message.message_id

# Handler for button 'next' -> void
async def button_next(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict = USER_SESSION.get(update.effective_user.id)
    i         = user_dict["index"] = user_dict["index"] + 1
    verbs_id  = user_dict["verbs_id"]
    verb_id   = verbs_id[i]
    prev_message_id = user_dict.get("message_id")

    if verbs_id:
        if i != (len(verbs_id) - 1):
            keyboard = [
                [
                    InlineKeyboardButton("Prev", callback_data="prev"),
                    InlineKeyboardButton("Next", callback_data="next"),
                ]
            ]
        else:
            keyboard = [
                [
                    InlineKeyboardButton("Prev", callback_data="prev"),
                    InlineKeyboardButton("Start test", callback_data="test_1"),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        image_path = IMAGE_PATH + str(verb_id) + '.png'
        img = get_image(image_path)

        new_message = await update.callback_query.message.reply_photo(photo=img, reply_markup=reply_markup)

        if prev_message_id:
            try:
                await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
            except Exception as e:
                print(f"Не удалось удалить предыдущее сообщение: {e}")

        user_dict["message_id"] = new_message.message_id
    else:
        await update.callback_query.message.reply_text("Проблема! Такого глагола не существует!")

# Handler for button 'prev' -> void
async def button_prev(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict = USER_SESSION.get(update.effective_user.id)
    i         = user_dict["index"] = user_dict["index"] - 1
    verb_id   = user_dict["verbs_id"][i]
    prev_message_id = user_dict.get("message_id")

    if i != 0:
        keyboard = [
            [
                InlineKeyboardButton("Prev", callback_data="prev"),
                InlineKeyboardButton("Next", callback_data="next"),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("Next", callback_data="next")
            ]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    image_path = IMAGE_PATH + str(verb_id) + '.png'
    img        = get_image(image_path)

    new_message = await update.callback_query.message.reply_photo(photo=img, reply_markup=reply_markup)

    if prev_message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
        except Exception as e:
            print(f"Не удалось удалить предыдущее сообщение: {e}")

    user_dict["message_id"] = new_message.message_id

# Handler for button 'test' irregular verbs test -> void
async def button_test_1(update, context: ContextTypes.DEFAULT_TYPE):
    user_id   = update.effective_user.id
    user_dict = USER_SESSION.get(user_id)
    verbs_id  = user_dict["verbs_id"]
    del USER_SESSION[user_id]
    await upd_usr_progress(user_id, verbs_id)

    prev_message_id = user_dict.get("message_id")

    if prev_message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
        except Exception as e:
            print(f"Не удалось удалить предыдущее сообщение: {e}")

    ## Временная часть
        await update.callback_query.message.reply_text("Пока здесь ничего нет! Но я запомнил ваш прогресс.")
    ##

# Handler for buttons
async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id

    try:
        if not is_session_active(user_id):
            await query.message.reply_text("Ваша сессия истекла. Начните новую с помощью команды /irregular_verbs.")
            return

        button_actions = {
            "ok": button_ok,
            "next": button_next,
            "prev": button_prev,
            "test_1": button_test_1
        }

        action = button_actions.get(query.data)
        if action:
            await action(update, context)
        else:
            await query.message.reply_text("Неизвестная команда. Попробуйте снова.")
    except Exception as e:
        print(f"Ошибка в button_handler: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")
#
## END BOTTOM SEGMENT


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    await app.bot.set_my_commands([
        BotCommand("start", "Начать работу с ботом"),
        BotCommand("help", "Список доступных команд"),
        BotCommand("irregular_verbs", "Изучить неправильные глаголы"),
    ])

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("irregular_verbs", irregular_verbs))
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