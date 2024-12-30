import aiosqlite

## SEARCH IRREGULAR VERBS
async def search_present_simple(verb, db_name):
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.execute("SELECT id, base_form FROM verbs")
        verbs  = await cursor.fetchall()

        for v in verbs:
            if v[1].startswith(verb):
                return v[0]
    return None

async def search_past_simple(verb, db_name):
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.execute("SELECT id, past_simple FROM verbs")
        row    = await cursor.fetchall()

        for id, verbs in row:
            parts = verbs.split(" ") # parts[0] = verbs, parts[1] = transcriptions
            part  = parts[0].split("/")
            if part[0] == verb or (len(part) > 1 and part[1] == verb):
                return id
    return None

async def search_past_participle(verb, db_name):
    async with aiosqlite.connect(db_name) as conn:
        cursor = await conn.execute("SELECT id, past_participle FROM verbs")
        row    = await cursor.fetchall()

        for id, verbs in row:
            parts = verbs.split(" ")  # parts[0] = verbs, parts[1] = transcriptions
            part = parts[0].split("/")
            if part[0] == verb or (len(part) > 1 and part[1] == verb):
                return id
    return None
## END SEARCH