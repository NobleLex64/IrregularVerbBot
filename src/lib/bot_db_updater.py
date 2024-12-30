import aiosqlite

from globals           import DB_NAME, VERBS_COUNT
from lib.bot_functions import set_bit


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