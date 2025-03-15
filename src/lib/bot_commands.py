import aiosqlite

from globals                     import DB_NAME, IMAGE_PATH, VERBS_COUNT, VERBS_ON_PAGE, USER_SESSION, TEXT_LIST, ADMIN_ID,CHANNEL_USERNAMES
from lib.bot_search_handler      import search_present_simple, search_past_simple, search_past_participle
from lib.bot_db_updater          import add_user_in_db
from lib.bot_functions           import find_next_unlearned, is_bit_set
from lib.bot_image_manager       import get_image
from lib.bot_session_manager     import is_session_active, start_user_session
from lib.bot_check_subscriptions import check_subscriptions, not_subscriptions

from telegram                    import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext                import ApplicationBuilder, ContextTypes, CallbackContext

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message :
        await update.callback_query.answer()

    if CHANNEL_USERNAMES and CHANNEL_USERNAMES != [""] and not await check_subscriptions(update, context):
        await not_subscriptions(update, context)
        return

    text = TEXT_LIST[0]
    keyboard = [
        [InlineKeyboardButton(TEXT_LIST[9], callback_data="help_command")],
        [InlineKeyboardButton(TEXT_LIST[10], callback_data="irregular_verbs")],
        [InlineKeyboardButton(TEXT_LIST[11], callback_data="table")],
        [InlineKeyboardButton(TEXT_LIST[12], callback_data="progress")],
    ]
    if ADMIN_ID and update.effective_user.id == int(ADMIN_ID):
        keyboard.append([InlineKeyboardButton("check students progress", callback_data="stud_progress")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        message = await update.message.reply_text(text, reply_markup=reply_markup)
        await update.message.delete()
    else:
        message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        await update.callback_query.message.delete()

# Command: /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    text = TEXT_LIST[1]
    keyboard = [
        [InlineKeyboardButton(TEXT_LIST[13], callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    await update.callback_query.message.delete()

# Command: /progress
async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    user_id   = update.effective_user.id
    user_name = update.effective_user.username
    await add_user_in_db(user_id, user_name)

    count = 0
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor   = await conn.execute("SELECT progress FROM users WHERE id = ?", (user_id,))
        row      = await cursor.fetchone()
        progress = bytearray(row[0])

        for i in range(0, len(progress)):
            if is_bit_set(progress, i):
                count += 1

    text = TEXT_LIST[4] + f"{count}/{len(progress) * 8}"
    keyboard = [
        [InlineKeyboardButton(TEXT_LIST[13], callback_data="start")],
        [InlineKeyboardButton(TEXT_LIST[15], callback_data="ask_delete_progress")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    await update.callback_query.message.delete()

# Command: /irregular_verbs
async def irregular_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if is_session_active(update.effective_user.id):
        keyboard = [
            [InlineKeyboardButton(TEXT_LIST[13], callback_data="start")],
            [InlineKeyboardButton(TEXT_LIST[16], callback_data="restart")]
        ]
        text = TEXT_LIST[6]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        await update.callback_query.message.delete()
        return

    try:
        user_id = update.effective_user.id
        user_name = update.effective_user.username

        await add_user_in_db(user_id, user_name)

        async with aiosqlite.connect(DB_NAME) as conn:
            cursor = await conn.execute("SELECT progress FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            progress = bytearray(row[0])

            verbs_indexes = find_next_unlearned(progress, 7)

            if len(verbs_indexes) == 0:
                message = await update.callback_query.message.reply_text("Вы уже изучили все доступные глаголы!")
                await update.callback_query.message.delete()
                return

        keyboard = [
            [InlineKeyboardButton(TEXT_LIST[17], callback_data="ok")],
            [InlineKeyboardButton(TEXT_LIST[13], callback_data="restart")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await update.callback_query.message.reply_text(
            TEXT_LIST[2],
            reply_markup=reply_markup
        )

        start_user_session(user_id, verbs_indexes, message.message_id)

        await update.callback_query.message.delete()

    except Exception as e:
        print(f"Ошибка: {e}")
        await update.callback_query.message.reply_text("Произошла ошибка при обработке команды.")
    except aiosqlite.Error as db_error:
        message = await update.callback_query.message.reply_text(f"Ошибка базы данных: {db_error}")
        await update.callback_query.message.delete()

# Command: /table
async def irregular_verbs_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if is_session_active(update.effective_user.id):
        keyboard = [
            [InlineKeyboardButton(TEXT_LIST[13], callback_data="start")],
            [InlineKeyboardButton(TEXT_LIST[14], callback_data="restart")]
        ]
        text = TEXT_LIST[6]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        await update.callback_query.message.delete()
        return

    try:
        user_id   = update.effective_user.id
        indexes   = []
        count_verbs = 0
        async with aiosqlite.connect(DB_NAME) as conn:
            cursor = await conn.execute("SELECT COUNT(*) FROM verbs")
            result = await cursor.fetchone()
            count_verbs = result[0]

        pages = 0
        if count_verbs % VERBS_ON_PAGE == 0:
            pages = count_verbs // VERBS_ON_PAGE
        else:
            pages = count_verbs // VERBS_ON_PAGE + 1
        for i in range(1, pages + 1):
            indexes.append(f"table_{i}")

        keyboard = [
            [InlineKeyboardButton(TEXT_LIST[18], callback_data="ok")],
            [InlineKeyboardButton(TEXT_LIST[13], callback_data="restart")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await update.callback_query.message.reply_text(
            TEXT_LIST[3],
            reply_markup=reply_markup
        )
        start_user_session(user_id, indexes, message.message_id)
        await update.callback_query.message.delete()

    except Exception as e:
        print(f"Ошибка: {e}")
        await update.callback_query.message.reply_text("Произошла ошибка при обработке команды.")

async def restart_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if is_session_active(update.effective_user.id):
        del USER_SESSION[update.effective_user.id]

    await start(update, context)

async def ask_delete_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    text = TEXT_LIST[5]
    keyboard = [
        [InlineKeyboardButton(TEXT_LIST[13], callback_data="progress")],
        [InlineKeyboardButton(TEXT_LIST[14], callback_data="delete_progress")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    await update.callback_query.message.delete()

async def delete_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with aiosqlite.connect(DB_NAME) as conn:
        await conn.execute("UPDATE users SET progress = ? WHERE id = ?", (bytearray(VERBS_COUNT // 8), user_id))
        await conn.commit()

    await progress_command(update, context)

async def echo(update: Update, context: CallbackContext):
    verb = update.message.text.lower()

    functions = [
        search_present_simple,
        search_past_simple,
        search_past_participle
    ]
    for function in functions:
        verb_id = await function(verb, DB_NAME)
        if verb_id:
            image_path = IMAGE_PATH + str(verb_id) + '.png'
            try:
                img = get_image(image_path)
                keyboard = [
                    [InlineKeyboardButton(TEXT_LIST[13], callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = await update.message.reply_photo(photo=img, reply_markup=reply_markup)
                return
            except Exception as e:
                await update.message.reply_text(f"Не удалось загрузить изображение: {e}")
                return

    await update.message.reply_text(f"Глагол {verb} не найден в базе данных.")

async def students_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = {}
    async with aiosqlite.connect(DB_NAME) as conn:
        cursor   = await conn.execute("SELECT username, progress FROM users")
        rows     = await cursor.fetchall()

        for name, progress in rows:
            count = sum(1 for i in range(len(progress) * 8) if is_bit_set(progress, i))
            result[name] = count

    text = ''

    for name, count in result.items():
        text += f"{name}: {count}\n"

    await update.callback_query.message.reply_text(text)