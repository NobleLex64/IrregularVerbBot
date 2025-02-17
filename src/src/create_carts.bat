@echo off
chcp 65001
cd /d "%~dp0"

:: Запуск Python-скриптов по очереди
echo Запуск скриптов по созданию карточек и юазы данных...

:: Запуск первого скрипта
python "initialization_data_base.py"
if errorlevel 1 (
    echo Ошибка при выполнении initialization_data_base.py
    pause
    exit /b 1
)

:: Запуск второго скрипта
python "create_irregular_verbs_carts.py"
if errorlevel 1 (
    echo Ошибка при выполнении create_irregular_verbs_carts.py
    pause
    exit /b 1
)


exit /b
