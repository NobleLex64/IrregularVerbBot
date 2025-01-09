import aiosqlite

from datetime import datetime
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
                        INSERT INTO users (id, access, username, progress, data_last_update)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        "new",
                        username, bytearray(VERBS_COUNT // 8),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
            )
            await conn.commit()
        else:
            async with aiosqlite.connect(DB_NAME) as conn:
                await conn.execute("UPDATE users SET data_last_update = ? WHERE id = ?",
                                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
                await conn.commit()

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