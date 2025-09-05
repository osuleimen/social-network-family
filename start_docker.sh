#!/bin/bash

echo "🚀 Запуск Social Network в Docker"
echo "=================================="

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: Запустите скрипт из директории social_network"
    exit 1
fi

# Проверяем наличие docker.env
if [ ! -f "docker.env" ]; then
    echo "❌ Ошибка: Файл docker.env не найден"
    exit 1
fi

echo "🔧 Останавливаем существующие контейнеры..."
docker-compose down

echo "🧹 Удаляем старые образы..."
docker-compose rm -f

echo "🔨 Пересобираем контейнеры..."
docker-compose build --no-cache

echo "🚀 Запускаем все сервисы..."
docker-compose up -d

echo "⏳ Ждем запуска сервисов..."
sleep 10

echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "🌐 Сервисы доступны по адресам:"
echo "   Backend API: http://localhost:5001"
echo "   Frontend:    http://localhost:3001"
echo "   Nginx:       http://localhost:8443"
echo "   PostgreSQL:  localhost:5433"
echo "   Redis:       localhost:6380"
echo ""
echo "📱 Для тестирования SMS-аутентификации:"
echo "   1. Откройте: http://localhost:3001/auth"
echo "   2. Введите номер: +77019990438"
echo "   3. Код будет показан в логах backend"
echo ""
echo "📋 Логи backend:"
echo "   docker-compose logs -f backend"
echo ""
echo "⏹️  Для остановки: docker-compose down"

