import aiosqlite

from globals                 import DB_NAME, IMAGE_PATH, VERBS_COUNT, VERBS_ON_PAGE
from lib.bot_search_handler  import search_present_simple, search_past_simple, search_past_participle
from lib.bot_db_updater      import add_user_in_db
from lib.bot_functions       import find_next_unlearned, is_bit_set
from lib.bot_image_manager   import get_image
from lib.bot_session_manager import is_session_active, start_user_session

from telegram                import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext            import ApplicationBuilder, ContextTypes, CallbackContext

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message :
        await update.callback_query.answer()

    text = f"Привет {update.effective_user.username}! Я бот для помощи с изучением английского языка."

    keyboard = [
        [InlineKeyboardButton("❓  Помощь", callback_data="help_command")],
        [InlineKeyboardButton("📔  Учить неправильные глаголы", callback_data="irregular_verbs")],
        [InlineKeyboardButton("🔣  Таблица неправильных глаголов", callback_data="table")],
        [InlineKeyboardButton("📈  Прогресс", callback_data="progress")],
    ]
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
    text = ''' 
        Привет! Я расскажу тебе, что я могу сделать.. 


    '⬅️ Back'
        - эта кнопка вернёт тебя на предыдущую старницу.

    '📔 Учить неправильные глаголы'
        - это кнопка поможет тебе выучить неправильные глаголы.
        - в общем предоставляет тебе 7 карточек с неправильными глаголами.
        - переключайся между карточками с помощью кнопок <<Prev>> <<Next>>.
        - когда выучищь все 7 карточек жми кнопку <<Learned!>>
        - карточки которые ты выучил добавятся в твой прогресс и больше тебе не попадутся!

    '🔣 Таблица неправильных глаголов'
        - это кнопка покажет тебе всю таблицу неправильных глаголов.
        - она содержит более 200 неправильных глаголов!
        - переключайся между страницами с помощью кнопок <<Prev>> <<Next>>.
        - когда закончишь просматривать таблицу жми <<Learned!>>.

    '📈  Прогресс'
        - эта команда покажет как много ты успел изучить и мколько еще осталось глаголов.
        - также она покажет в какие дни и сколько глаголов ты выучил!
        
    p.s.
        Попробуй написать в чат неправильный глагол...
    '''
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data="start")]
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

        for i in range(0, VERBS_COUNT):
            if is_bit_set(progress, i):
                count += 1

    text = f"Your progress: {count}/200"
    keyboard = [
        [InlineKeyboardButton("⬅️ Back", callback_data="start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    await update.callback_query.message.delete()

# Command: /irregular_verbs
async def irregular_verbs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if is_session_active(update.effective_user.id):
        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data="start")]
        ]
        text = "Команда уже активна. Завершите текущую сессию, чтобы начать новую."
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
            [
                InlineKeyboardButton("Приступить к выполнению", callback_data="ok"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await update.callback_query.message.reply_text(
            "Вы готовы начать изучение следующего набора глаголов?",
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
    except Exception as e:
        message = await update.callback_query.message.reply_text(f"Произошла ошибка: {e}")
        await update.callback_query.message.delete()

# Command: /table
async def irregular_verbs_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    if is_session_active(update.effective_user.id):
        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data="start")]
        ]
        text = "Команда уже активна. Завершите текущую сессию, чтобы начать новую."
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
            [
                InlineKeyboardButton("Получить?", callback_data="ok"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = await update.callback_query.message.reply_text(
            "Хотите получить таблицу неправильных глаголов?",
            reply_markup=reply_markup
        )
        start_user_session(user_id, indexes, message.message_id)
        await update.callback_query.message.delete()

    except Exception as e:
        print(f"Ошибка: {e}")
        await update.callback_query.message.reply_text("Произошла ошибка при обработке команды.")

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
                    [InlineKeyboardButton("⬅️ Back", callback_data="start")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                message = await update.message.reply_photo(photo=img, reply_markup=reply_markup)
                return
            except Exception as e:
                await update.message.reply_text(f"Не удалось загрузить изображение: {e}")
                return

    await update.message.reply_text(f"Глагол {verb} не найден в базе данных.")