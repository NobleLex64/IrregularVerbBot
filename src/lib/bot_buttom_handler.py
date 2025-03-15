from telegram                    import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, ReplyKeyboardMarkup
from telegram.ext                import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, CallbackContext

from lib.bot_verbs_test          import test, correct_quiz, incorrect_quiz
from lib.bot_check_subscriptions import check_subscriptions, not_subscriptions
from lib.bot_commands            import help_command, irregular_verbs, start, progress_command, irregular_verbs_table, restart_session, ask_delete_progress, delete_progress, students_progress
from lib.bot_image_manager       import get_image
from lib.bot_session_manager     import is_session_active
from globals                     import USER_SESSION, IMAGE_PATH, TEXT_LIST


async def send_button_interface(update, context, verb_id, keyboard, user_dict, prev_message_id):
    if verb_id:
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

## START BUTTON HANDLER SEGMENT
# Handler for button 'ok' -> void
async def button_ok(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict  = USER_SESSION.get(update.effective_user.id)
    verb_id   = user_dict.get("verbs_id")[0]
    prev_message_id = user_dict.get("message_id")
    keyboard = [
        [
            InlineKeyboardButton(TEXT_LIST[13], callback_data="restart"),
            InlineKeyboardButton(TEXT_LIST[19], callback_data="next")
        ]
    ]

    await send_button_interface(update, context, verb_id, keyboard, user_dict, prev_message_id)

# Handler for button 'next' -> void
async def button_next(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict = USER_SESSION.get(update.effective_user.id)
    i         = user_dict["index"] = user_dict["index"] + 1
    verbs_id  = user_dict["verbs_id"]
    verb_id   = verbs_id[i]
    prev_message_id = user_dict.get("message_id")

    if i != (len(verbs_id) - 1):
        keyboard = [
            [
                InlineKeyboardButton(TEXT_LIST[20], callback_data="prev"),
                InlineKeyboardButton(TEXT_LIST[19], callback_data="next"),
            ],
            [
                InlineKeyboardButton(TEXT_LIST[13], callback_data="restart"),
            ]
        ]
    else:
        type_id = 0
        text = [ [TEXT_LIST[22], "test"], [TEXT_LIST[21], "restart"] ]
        if not str(verbs_id[0]).isdigit():
            type_id = 1
        keyboard = [
            [
                InlineKeyboardButton(TEXT_LIST[20], callback_data="prev"),
                InlineKeyboardButton(text[type_id][0], callback_data=text[type_id][1]),
            ]
        ]

    await send_button_interface(update, context, verb_id, keyboard, user_dict, prev_message_id)

# Handler for button 'prev' -> void
async def button_prev(update, context: ContextTypes.DEFAULT_TYPE):
    user_dict = USER_SESSION.get(update.effective_user.id)
    i         = user_dict["index"] = user_dict["index"] - 1
    verb_id   = user_dict["verbs_id"][i]
    prev_message_id = user_dict.get("message_id")

    if i != 0:
        keyboard = [
            [
                InlineKeyboardButton(TEXT_LIST[20], callback_data="prev"),
                InlineKeyboardButton(TEXT_LIST[19], callback_data="next"),
            ],
            [
                InlineKeyboardButton(TEXT_LIST[13], callback_data="restart"),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(TEXT_LIST[13], callback_data="restart"),
                InlineKeyboardButton(TEXT_LIST[19], callback_data="next")
            ]
        ]

    await send_button_interface(update, context, verb_id, keyboard, user_dict, prev_message_id)

# Handler for button 'test' irregular verbs test -> void
async def button_test(update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

    user_id         = update.effective_user.id
    user_dict       = USER_SESSION.get(user_id)
    prev_message_id = user_dict["message_id"]

    if prev_message_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=prev_message_id)
        except Exception as e:
            print(f"Не удалось удалить предыдущее сообщение: {e}")

    user_dict["message_id"] = 0
    user_dict["index"] = 0
    await test(update, context)

# Handler for buttons
async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    qdata = query.data

    if qdata == "check_subscriptions":
        if await check_subscriptions(update, context):
            await start(update, context)
        else:
            await not_subscriptions(update, context)
        return

    button_actions = {
        "ok": button_ok,
        "next": button_next,
        "prev": button_prev,
        "test": button_test,
        "correct": correct_quiz,
        "incorrect": incorrect_quiz
    }

    button_command = {
        "help_command": help_command,
        "irregular_verbs": irregular_verbs,
        "start": start,
        "progress": progress_command,
        "table": irregular_verbs_table,
        "restart": restart_session,
        "ask_delete_progress": ask_delete_progress,
        "delete_progress": delete_progress,
        "stud_progress": students_progress
    }

    try:
        user_id                = update.effective_user.id
        if button_actions.get(qdata) and not is_session_active(user_id):
            keyboard = [[InlineKeyboardButton(TEXT_LIST[21], callback_data="start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = TEXT_LIST[7]
            message = await query.message.reply_text(text, reply_markup=reply_markup)
            await query.message.delete()
            return

        if button_actions.get(qdata):
            action = button_actions.get(qdata)
        else:
            action = button_command.get(qdata)

        if action:
            await action(update, context)
        else:
            await query.message.reply_text("Неизвестная команда. Попробуйте снова.")
    except Exception as e:
        print(f"Ошибка в button_handler: {e}")
        await query.message.reply_text("Произошла ошибка. Попробуйте снова.")
#
## END BOTTOM SEGMENT