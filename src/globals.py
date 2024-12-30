import os
from datetime import timedelta
from dotenv   import load_dotenv

load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")
DB_NAME         = os.getenv("DB_NAME")
IMAGE_PATH      = os.getenv("IMAGE_PATH")
VERBS_COUNT     = int(os.getenv("VERBS_COUNT"))
VERBS_ON_PAGE   = int(os.getenv("VERB_ON_PAGE"))
USER_SESSION    = {}
image_cache     = {}
SESSION_TIMEOUT = timedelta(minutes=10)
TTL             = 86400  # 24 часа
VERBS_WORK      = False

if not IMAGE_PATH:
    raise ValueError("Путь к файду не найден! Убедитесь, что файл .env существует и содержит IMAGE_PATH.")

if not DB_NAME:
    raise ValueError("Имя базы данных не найденно! Убедитесь, что файл .env существует и содержит DB_NAME.")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден! Убедитесь, что файл .env существует и содержит BOT_TOKEN.")

if not VERBS_COUNT:
    raise ValueError("VERBS_COUNT не найден! Убедитесь, что файл .env существует и содержит VERBS_COUNT.")

if not VERBS_ON_PAGE:
    raise ValueError("VERBS_ON_PAGE не найден! Убедитесь, что файл .env существует и содержит VERB_ON_PAGE.")