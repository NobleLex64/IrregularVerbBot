import asyncio

from globals   import USER_SESSION, SESSION_TIMEOUT
from datetime  import datetime

# Start a session for a user
def start_user_session(user_id, verbs_indexes, mes_id):
    USER_SESSION[user_id] = {
        "verbs_id": verbs_indexes,
        "message_id": mes_id,
        "index": 0,
        "start_time": datetime.now(),
    }

# Check if a user's session is still active
def is_session_active(user_id):
    session = USER_SESSION.get(user_id)
    if not session:
        return False
    return datetime.now() - session["start_time"] < SESSION_TIMEOUT

# Remove expired sessions
async def clear_expired_sessions():
    now = datetime.now()
    expired_users = [
        user_id for user_id, session in USER_SESSION.items()
        if now - session["start_time"] > SESSION_TIMEOUT
    ]
    for user_id in expired_users:
        del USER_SESSION[user_id]

# Periodically clean up expired sessions
async def clean_up_sessions():
    while True:
        try:
            await clear_expired_sessions()
        except Exception as e:
            print(f"Error during session cleanup: {e}")
        await asyncio.sleep(120)  # Cleanup every 2 minutes
