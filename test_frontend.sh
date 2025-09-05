#!/bin/bash

echo "🚀 Тестирование SMS-аутентификации Frontend"
echo "=========================================="

# Проверяем, что мы в правильной директории
if [ ! -f "social_network/frontend/package.json" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории проекта"
    exit 1
fi

echo "📱 Переходим в директорию frontend..."
cd social_network/frontend

echo "🔧 Проверяем зависимости..."
if [ ! -d "node_modules" ]; then
    echo "📦 Устанавливаем зависимости..."
    npm install
fi

echo "🌐 Запускаем frontend в режиме разработки..."
echo "📋 Откройте браузер и перейдите на: http://localhost:5173/auth"
echo "📱 Введите тестовый номер: +77019990438"
echo "🔐 Код подтверждения будет показан в консоли браузера (F12 → Console)"
echo ""
echo "⏹️  Для остановки нажмите Ctrl+C"
echo ""

npm run dev

