import aiosqlite

from lib.bot_db_updater import add_user_in_db
from globals            import DB_NAME, CHANNEL_USERNAME
from telegram           import Update,InlineKeyboardButton, InlineKeyboardMarkup, Bot


async def check_subscriptions(update, context):
    user_id = update.effective_user.id
    user_name = update.effective_user.name

    bot: BOT = context.bot

    try:
        # Проверка статуса пользователя в канале
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        status = member.status
        if status in ["member", "administrator", "creator"]:
            async with aiosqlite.connect(DB_NAME) as conn:
                cursor = await conn.execute("SELECT access FROM users WHERE id = ?", (user_id,))
                row = await cursor.fetchone()

                if row is None:
                    await add_user_in_db(user_id, user_name)
                elif row != "student" or row != "admin":
                    await conn.execute("UPDATE users SET access = ? WHERE id = ?", ("student", user_id))
                    await conn.commit()
        else:
            return False
    except Exception as e:
        await update.callback_query.message.reply_text(f"Ошибка при проверке подписки: {e}")
        return False

    return True

async def not_subscriptions(update, context):
    if not update.message :
        await update.callback_query.answer()

    text = f"Привет {update.effective_user.username} ты еще не подписался на канал! Прежде чем начать пользоваться моим функционалом подпишись на {CHANNEL_USERNAME}!."

    keyboard = [
        [InlineKeyboardButton("Я подписался!", callback_data="check_subscriptions")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        message = await update.message.reply_text(text, reply_markup=reply_markup)
        await update.message.delete()
    else:
        message = await update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        await update.callback_query.message.delete()
