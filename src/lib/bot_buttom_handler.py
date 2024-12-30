from telegram             import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup
from telegram.ext         import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, CallbackContext

from lib.bot_commands        import help_command, irregular_verbs, start, progress_command, irregular_verbs_table
from lib.bot_db_updater      import upd_usr_progress
from lib.bot_image_manager   import get_image
from lib.bot_session_manager import is_session_active
from globals                 import USER_SESSION, IMAGE_PATH


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
                    InlineKeyboardButton("Learned!", callback_data="test_1"),
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
    await update.callback_query.answer()
    user_id   = update.effective_user.id
    user_dict = USER_SESSION.get(user_id)
    verbs_id  = user_dict["verbs_id"]
    del USER_SESSION[user_id]
    if str(verbs_id[0]).isdigit():
        await upd_usr_progress(user_id, verbs_id)

    prev_message_id = user_dict.get("message_id")

    if prev_message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
        except Exception as e:
            print(f"Не удалось удалить предыдущее сообщение: {e}")

    ## Временная часть
        keyboard = [[InlineKeyboardButton("Меню", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Пока здесь ничего нет! Но я запомнил ваш прогресс."
        message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
    ##

# Handler for buttons
async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "help_command":
        await help_command(update, context)
        return
    elif query.data == "irregular_verbs":
        await irregular_verbs(update, context)
        return
    elif query.data == "start":
        await start(update, context)
        return
    elif query.data == "progress":
        await progress_command(update, context)
        return
    elif query.data == "table":
        await irregular_verbs_table(update, context)
        return

    user_id = update.effective_user.id

    try:
        if not is_session_active(user_id):
            keyboard = [[InlineKeyboardButton("Меню", callback_data="start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = "Ваша сессия истекла. Начните новую."
            message = await update.message.reply_text(text, reply_markup=reply_markup)
            await update.message.delete()
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