#!/bin/bash

set -e  # Прекратить выполнение при ошибке

cd "$(dirname "$0")"

echo "Проверка папок..."

mkdir -p "data/DataBase"
echo "Папка data/DataBase создана или уже существует."

mkdir -p "data/IrregularVerbCarts"
echo "Папка data/IrregularVerbCarts создана или уже существует."

mkdir -p "src/data/BackgroundImage"
echo "Папка src/data/BackgroundImage создана или уже существует."

echo "Введите значение для BOT_TOKEN:"
read -r BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "BOT_TOKEN не может быть пустым. Попробуйте снова."
    exit 1
fi

echo "Введите значение для CHANNEL_USERNAME:"
read -r CHANNEL
if [ -z "$CHANNEL" ]; then
    echo "CHANNEL_USERNAME не может быть пустым. Попробуйте снова."
    exit 1
fi

env_file="src/.env"
if [ ! -f "$env_file" ]; then
    cat > "$env_file" <<EOL
BOT_TOKEN=$BOT_TOKEN
DB_NAME=../data/DataBase/EnLessonsBot.db
VERBS_COUNT=160
IMAGE_PATH=../data/IrregularVerbCarts/
VERB_ON_PAGE=15
CHANNEL_USERNAME=$CHANNEL
EOL
    echo "Файл .env создан в src/."
else
    echo "Файл .env уже существует."
fi

env_file_src="src/src/.env"
if [ ! -f "$env_file_src" ]; then
    cat > "$env_file_src" <<EOL
DB_PATH=../../data/DataBase/EnLessonsBot.db
SQL_GET=../../data/sqlite_verbs.txt
IRREGULAR_VERB_CARDS_PATH=../../data/IrregularVerbCarts/
BACKGROUND_IMG_PATH=../data/BackgroundImage/

VERB_ON_PAGE=15

VERB_TEXT_COLOR=0xDC140C
VERB_TRANSLATION_COLOR=0x228B22
FONT=arial.ttf

CARTS_WIDTH=800
CARTS_HEIGHT=450
CARTS_BACKGROUND_COLOR=0xFFFFFFE0
CARTS_TEXT_SIZE=40

TABLE_WIDTH=1600
TABLE_HEIGHT=900
TABLE_BACKGROUND_COLOR=0xFFFFFF00
TABLE_HEADER_TEXT_COLOR=0x4040FF
TABLE_HEADER_TEXT_SIZE=30
TABLE_TEXT_SIZE=25
EOL
    echo "Файл .env создан в src/src/."
else
    echo "Файл .env уже существует."
fi

echo "Установка зависимостей..."
pip install python-dotenv Pillow aiofiles aiosqlite nest-asyncio asyncio python-telegram-bot
if [ $? -ne 0 ]; then
    echo "Ошибка при установке библиотек."
    exit 1
fi

# Запуск create_carts.sh
if ! bash "src/src/create_carts.sh"; then
    echo "Ошибка при выполнении create_carts.sh"
    exit 1
fi

# Запуск start.sh
if ! bash "src/start.sh"; then
    echo "Ошибка при выполнении start.sh"
    exit 1
fi

echo "Скрипт выполнен успешно."
