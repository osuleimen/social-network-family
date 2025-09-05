#!/bin/bash

echo "🚀 Запуск Backend для тестирования SMS-аутентификации"
echo "====================================================="

# Проверяем, что мы в правильной директории
if [ ! -f "social_network/backend/run.py" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "🔧 Переходим в директорию backend..."
cd social_network/backend

echo "🐍 Проверяем Python окружение..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

echo "📦 Проверяем зависимости..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден"
    exit 1
fi

echo "🔧 Устанавливаем зависимости..."
pip3 install -r requirements.txt

echo "🌐 Запускаем backend в режиме разработки..."
echo "📋 API будет доступен по адресу: http://localhost:5000"
echo "📱 Тестовый номер: +77019990438"
echo "🔐 Коды подтверждения будут показаны в логах"
echo ""
echo "⏹️  Для остановки нажмите Ctrl+C"
echo ""

# Устанавливаем переменные окружения для разработки
export FLASK_ENV=development
export FLASK_DEBUG=1
export MOBIZON_API_KEY=7788b3700803c6a924862ad070d47013b403e20b

python3 run.py

