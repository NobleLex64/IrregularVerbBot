@echo off

chcp 65001
cd /d "%~dp0"

:: Проверка и создание папок
echo Проверка папок...


if not exist "data/DataBase" (
    mkdir "data/DataBase"
    echo Папка data/DataBase создана.
) else (
    echo Папка data/DataBase уже существует.
)

if not exist "data/IrregularVerbCarts" (
    mkdir "data/IrregularVerbCarts"
    echo Папка data/IrregularVerbCarts создана.
) else (
    echo Папка data/IrregularVerbCarts уже существует.
)

if not exist "src/data/BackgroundImage" (
    mkdir "src/data/BackgroundImage"
    echo Папка src/data/BackgroundImage создана.
) else (
    echo Папка src/data/BackgroundImage уже существует.
)

:: Проверка и создание файлов с текстом
echo Проверка файлов и запись текста...

echo Введите значение для BOT_TOKEN:
set /p BOT_TOKEN=
if "%BOT_TOKEN%"=="" (
    echo BOT_TOKEN не может быть пустым. Попробуйте снова.
    goto input_loop
)

if not exist ".\src\.env" (
    (
    echo BOT_TOKEN=%BOT_TOKEN%
    echo DB_NAME=../data/DataBase/EnLessonsBot.db
    echo VERBS_COUNT=256
    echo IMAGE_PATH=../data/IrregularVerbCarts/
    ) > ".\src\.env"
    echo Файл .env создан в ".\src\".
) else (
    echo Файл .env уже существует.
)

:: Создание файла ".\src\src\.env"
if not exist ".\src\src\.env" (
    (
    echo DB_PATH=../../data/DataBase/EnLessonsBot.db
    echo SQL_GET=../../data/sqlite_verbs.txt
    echo IRREGULAR_VERB_CARDS_PATH=../../data/IrregularVerbCarts/
    echo BACKGROUND_IMG_PATH=../data/BackgroundImage/
    echo WIDTH=800
    echo HEIGHT=450
    echo HEX_BACKGROUND_RGB=0xE4EEFB
    echo ALPHA=200
    echo HEX_TEXT_RGB=0xDC140C
    echo HEX_LAST_WORD_RGB=0x228B22
    echo FONT=arial.ttf
    echo TEXT_SIZE=40
    ) > ".\src\src\.env"
    echo Файл .env создан в ".\src\src\".
) else (
    echo Файл .env уже существует.
)

pip install python-dotenv Pillow aiofiles aiosqlite nest-asyncio asyncio python-telegram-bot
if %errorlevel% neq 0 (
    echo Ошибка при установке библиотек.
    pause
    exit /b
)

call "%~dp0src\src\start.bat"
call "%~dp0src\start.bat"


echo Все задачи выполнены успешно.
pause
