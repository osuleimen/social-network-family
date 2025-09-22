# Social Network Family

Современная социальная сеть для семей с поддержкой многоязычности (казахский, английский, русский языки).

## 🚀 Особенности

- **Многоязычность**: Поддержка казахского, английского и русского языков
- **Семейные связи**: Управление семейными отношениями и генеалогией
- **AI интеграция**: Автоматическое создание описаний постов с помощью Gemini AI
- **Медиа**: Загрузка и управление фотографиями и видео
- **Уведомления**: Система уведомлений в реальном времени
- **OAuth**: Авторизация через Google
- **SMS**: Отправка SMS через Mobizon API
- **Email**: Отправка email уведомлений

## 🏗️ Архитектура

### Backend (Flask)
- **Flask** - веб-фреймворк
- **SQLAlchemy** - ORM для работы с базой данных
- **PostgreSQL** - основная база данных
- **Redis** - кэширование и сессии
- **JWT** - аутентификация
- **Flask-Mail** - отправка email
- **Google OAuth** - авторизация через Google

### Frontend (React + TypeScript)
- **React 18** - пользовательский интерфейс
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **Axios** - HTTP клиент
- **React Router** - маршрутизация
- **React Query** - управление состоянием

### AI и внешние сервисы
- **Google Gemini AI** - генерация описаний постов
- **Mobizon API** - отправка SMS
- **Google OAuth** - авторизация

## 📋 Требования

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker (опционально)

## 🛠️ Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/social-network-family.git
cd social-network-family
```

### 2. Настройка Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Скопируйте `env.example` в `.env` и настройте переменные:

```bash
cp env.example .env
```

Обязательные переменные:
```env
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
POSTGRES_PASSWORD=your-secure-password
```

Опциональные переменные:
```env
GEMINI_API_KEY=your-gemini-api-key
MOBIZON_API_KEY=your-mobizon-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MAIL_PASSWORD=your-email-password
```

### 4. Настройка базы данных

```bash
# Создание базы данных
createdb social_network

# Запуск миграций
flask db upgrade
```

### 5. Настройка Frontend

```bash
cd frontend
npm install
```

### 6. Запуск приложения

#### Backend
```bash
cd backend
python run.py
```

#### Frontend
```bash
cd frontend
npm run dev
```

## 🐳 Docker

Для запуска с Docker:

```bash
# Создание .env файла для Docker
cp docker.env.example .env

# Запуск всех сервисов
docker-compose up -d
```

## 📱 API Endpoints

### Аутентификация
- `POST /api/auth/register` - регистрация
- `POST /api/auth/login` - вход
- `POST /api/auth/refresh` - обновление токена
- `GET /api/auth/google` - Google OAuth
- `GET /api/auth/google/callback` - Google OAuth callback

### Пользователи
- `GET /api/users/me` - текущий пользователь
- `PUT /api/users/me` - обновление профиля
- `GET /api/users/search` - поиск пользователей

### Посты
- `GET /api/posts` - список постов
- `POST /api/posts` - создание поста
- `GET /api/posts/{id}` - получение поста
- `PUT /api/posts/{id}` - обновление поста
- `DELETE /api/posts/{id}` - удаление поста

### Медиа
- `POST /api/media/upload` - загрузка медиа
- `GET /api/media/{id}` - получение медиа

## 🌐 Многоязычность

Приложение поддерживает 3 языка:
- **kk** - қазақ тілі (казахский)
- **en** - English (английский)
- **ru** - русский

Переключение языка происходит через интерфейс пользователя.

## 🤖 AI функции

- **Автогенерация описаний**: AI анализирует загруженные изображения и создает описания
- **Генерация хэштегов**: AI предлагает релевантные хэштеги
- **Улучшение контента**: AI может улучшить текст поста

## 📧 Уведомления

- **Email**: Отправка уведомлений на email
- **SMS**: Отправка SMS через Mobizon API
- **In-app**: Уведомления в приложении

## 🔒 Безопасность

- JWT токены для аутентификации
- Хэширование паролей
- CORS настройки
- Валидация входных данных
- Защита от CSRF атак

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Если у вас есть вопросы или проблемы, создайте Issue в репозитории.

## 🚀 Развертывание

Для продакшена рекомендуется использовать:
- Nginx как reverse proxy
- PostgreSQL как основная БД
- Redis для кэширования
- SSL сертификаты
- Мониторинг и логирование