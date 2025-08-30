# Инструкции по развертыванию

## Локальное развертывание

### Предварительные требования

1. **Docker и Docker Compose**
   - Установите Docker: https://docs.docker.com/get-docker/
   - Установите Docker Compose: https://docs.docker.com/compose/install/

2. **Git**
   - Установите Git: https://git-scm.com/downloads

### Быстрый запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd social_network
   ```

2. **Запустите приложение:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

3. **Откройте браузер:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

### Ручной запуск

1. **Настройте переменные окружения:**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл
   ```

2. **Запустите базу данных:**
   ```bash
   docker-compose up -d postgres redis
   ```

3. **Запустите бэкенд:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

4. **Запустите фронтенд (в новом терминале):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Развертывание на сервере

### Vercel (Frontend)

1. **Подготовьте проект:**
   ```bash
   cd frontend
   npm run build
   ```

2. **Создайте аккаунт на Vercel:**
   - Перейдите на https://vercel.com
   - Подключите ваш GitHub репозиторий

3. **Настройте переменные окружения:**
   - `VITE_API_URL`: URL вашего API

4. **Деплой:**
   - Vercel автоматически деплоит при каждом push в main ветку

### Railway (Backend)

1. **Создайте аккаунт на Railway:**
   - Перейдите на https://railway.app
   - Подключите ваш GitHub репозиторий

2. **Настройте переменные окружения:**
   ```
   FLASK_ENV=production
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret-key
   ```

3. **Деплой:**
   - Railway автоматически деплоит при каждом push

### Heroku

1. **Установите Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Ubuntu
   sudo snap install heroku --classic
   ```

2. **Создайте приложение:**
   ```bash
   heroku create your-app-name
   ```

3. **Добавьте PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

4. **Настройте переменные окружения:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set JWT_SECRET_KEY=your-jwt-secret-key
   ```

5. **Деплой:**
   ```bash
   git push heroku main
   ```

### DigitalOcean App Platform

1. **Создайте аккаунт на DigitalOcean:**
   - Перейдите на https://cloud.digitalocean.com

2. **Создайте новое приложение:**
   - Выберите ваш GitHub репозиторий
   - Настройте переменные окружения
   - Выберите план

3. **Деплой:**
   - DigitalOcean автоматически деплоит при каждом push

## Настройка домена

### Настройка DNS

1. **Добавьте A запись:**
   ```
   Type: A
   Name: @
   Value: <your-server-ip>
   ```

2. **Добавьте CNAME запись для www:**
   ```
   Type: CNAME
   Name: www
   Value: your-domain.com
   ```

### SSL сертификат

1. **Let's Encrypt (бесплатно):**
   ```bash
   sudo apt install certbot
   sudo certbot --nginx -d your-domain.com
   ```

2. **Автоматическое обновление:**
   ```bash
   sudo crontab -e
   # Добавьте строку:
   0 12 * * * /usr/bin/certbot renew --quiet
   ```

## Мониторинг и логирование

### Логи

```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Мониторинг

1. **Prometheus + Grafana:**
   - Добавьте мониторинг в docker-compose.yml
   - Настройте метрики для Flask приложения

2. **Sentry (ошибки):**
   - Зарегистрируйтесь на https://sentry.io
   - Добавьте SDK в приложение

## Резервное копирование

### База данных

```bash
# Создание бэкапа
docker-compose exec postgres pg_dump -U postgres social_network > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U postgres social_network < backup.sql
```

### Автоматическое резервное копирование

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres social_network > backup_$DATE.sql
```

## Масштабирование

### Горизонтальное масштабирование

```bash
# Увеличьте количество воркеров
docker-compose up --scale backend=3
```

### Load Balancer

```nginx
upstream backend {
    server backend1:5000;
    server backend2:5000;
    server backend3:5000;
}
```

## Безопасность

### Переменные окружения

- Никогда не коммитьте .env файлы
- Используйте секреты в production
- Регулярно обновляйте ключи

### Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Обновления

```bash
# Обновление приложения
git pull origin main
docker-compose down
docker-compose up --build -d
```

## Устранение неполадок

### Проблемы с подключением к базе данных

```bash
# Проверка статуса
docker-compose ps

# Перезапуск базы данных
docker-compose restart postgres
```

### Проблемы с памятью

```bash
# Очистка Docker
docker system prune -a

# Увеличение памяти для Docker
# В Docker Desktop: Settings -> Resources -> Memory
```

### Проблемы с производительностью

1. **Кэширование:**
   - Настройте Redis кэширование
   - Используйте CDN для статических файлов

2. **Оптимизация базы данных:**
   - Добавьте индексы
   - Настройте connection pooling

3. **Мониторинг:**
   - Используйте профилирование
   - Отслеживайте медленные запросы
