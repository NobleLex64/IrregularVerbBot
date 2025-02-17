#!/bin/bash

set -e  # Прекратить выполнение при ошибке

cd "$(dirname "$0")"

echo "Запуск скриптов по созданию карточек и базы данных..."

# Запуск первого скрипта
if ! python3 "initialization_data_base.py"; then
    echo "Ошибка при выполнении initialization_data_base.py"
    exit 1
fi

# Запуск второго скрипта
if ! python3 "create_irregular_verbs_carts.py"; then
    echo "Ошибка при выполнении create_irregular_verbs_carts.py"
    exit 1
fi

exit 0