#!/bin/bash

set -e  # Прекратить выполнение при ошибке

cd "$(dirname "$0")"

echo "Запуск бота...\n"

if ! python3 "main.py"; then
    echo "Ошибка при выполнении main.py"
    exit 1
fi