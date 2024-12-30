@echo off
chcp 65001
cd /d "%~dp0"

:: Запуск Python-скриптов по очереди
echo Запуск скриптов по созданию бота...

python main.py
if errorlevel 1 (
    echo Ошибка при выполнении main.py
    pause
    exit /b 1
)

exit /b