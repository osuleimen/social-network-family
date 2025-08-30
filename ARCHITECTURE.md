# Архитектура проекта

## Обзор системы

Социальная сеть построена на основе микросервисной архитектуры с использованием современных технологий и лучших практик разработки.

## Диаграмма архитектуры

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ - TypeScript    │    │ - Python        │    │ - Users         │
│ - Tailwind CSS  │    │ - SQLAlchemy    │    │ - Posts         │
│ - React Query   │    │ - JWT Auth      │    │ - Comments      │
│ - React Router  │    │ - Marshmallow   │    │ - Likes         │
└─────────────────┘    └─────────────────┘    │ - Follows       │
                                             │ - Notifications │
┌─────────────────┐    ┌─────────────────┐    └─────────────────┘
│   Nginx         │    │   Redis         │
│   (Proxy)       │    │   (Cache)       │
│                 │    │                 │
│ - Load Balancer │    │ - Sessions      │
│ - SSL/TLS       │    │ - Cache         │
│ - Static Files  │    │ - Celery Tasks  │
└─────────────────┘    └─────────────────┘
```

## Компоненты системы

### 1. Frontend (React + TypeScript)

**Технологии:**
- React 18 с TypeScript
- Vite для сборки и dev-сервера
- Tailwind CSS для стилизации
- React Query для управления состоянием
- React Router для навигации
- React Hook Form для форм
- Zod для валидации

**Структура:**
```
frontend/
├── src/
│   ├── components/     # Переиспользуемые компоненты
│   ├── pages/         # Страницы приложения
│   ├── contexts/      # React контексты
│   ├── hooks/         # Кастомные хуки
│   ├── services/      # API сервисы
│   ├── types/         # TypeScript типы
│   └── utils/         # Утилиты
├── public/            # Статические файлы
└── dist/              # Собранное приложение
```

**Ключевые особенности:**
- Полная типизация с TypeScript
- Современный UI с Tailwind CSS
- Темная/светлая тема
- Responsive дизайн
- Оптимизация производительности

### 2. Backend API (Flask + Python)

**Технологии:**
- Flask веб-фреймворк
- SQLAlchemy ORM
- Flask-JWT-Extended для аутентификации
- Marshmallow для сериализации
- Celery для асинхронных задач
- PostgreSQL как основная БД
- Redis для кэширования

**Структура:**
```
backend/
├── app/
│   ├── models/        # Модели данных
│   ├── api/           # API endpoints
│   ├── auth/          # Аутентификация
│   └── utils/         # Утилиты
├── migrations/        # Миграции БД
└── tests/            # Тесты
```

**API Endpoints:**
- `/api/auth/*` - Аутентификация
- `/api/users/*` - Управление пользователями
- `/api/posts/*` - Управление постами
- `/api/feed/*` - Лента и поиск

### 3. База данных (PostgreSQL)

**Схема данных:**
```sql
-- Пользователи
users (
  id, username, email, password_hash,
  first_name, last_name, bio, avatar_url,
  gramps_person_id, gramps_tree_id,
  created_at, updated_at
)

-- Посты
posts (
  id, content, author_id, is_public,
  created_at, updated_at
)

-- Комментарии
comments (
  id, content, author_id, post_id,
  parent_id, created_at, updated_at
)

-- Лайки
likes (
  id, user_id, post_id, created_at
)

-- Подписки
follows (
  id, follower_id, followed_id, created_at
)

-- Уведомления
notifications (
  id, user_id, type, title, message,
  data, is_read, created_at
)
```

**Индексы:**
- `users(username)` - уникальный индекс
- `users(email)` - уникальный индекс
- `posts(author_id, created_at)` - для ленты
- `likes(user_id, post_id)` - уникальный индекс
- `follows(follower_id, followed_id)` - уникальный индекс

### 4. Кэширование (Redis)

**Использование:**
- Сессии пользователей
- Кэширование частых запросов
- Очереди для Celery задач
- Временные данные

### 5. Веб-сервер (Nginx)

**Функции:**
- Reverse proxy для API и фронтенда
- SSL/TLS терминация
- Статические файлы
- Load balancing
- Rate limiting

## Паттерны проектирования

### 1. Repository Pattern
```python
class UserRepository:
    def get_by_id(self, user_id: int) -> User:
        return User.query.get(user_id)
    
    def create(self, user_data: dict) -> User:
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user
```

### 2. Service Layer Pattern
```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def create_user(self, user_data: dict) -> User:
        # Бизнес-логика
        return self.user_repo.create(user_data)
```

### 3. Factory Pattern
```python
def create_app(config_name=None):
    app = Flask(__name__)
    # Конфигурация
    return app
```

### 4. Observer Pattern (уведомления)
```python
class NotificationService:
    def notify_like(self, post: Post, user: User):
        notification = Notification(
            user_id=post.author_id,
            type='like',
            title='New Like',
            message=f'{user.first_name} liked your post'
        )
        db.session.add(notification)
        db.session.commit()
```

## Безопасность

### 1. Аутентификация
- JWT токены с refresh механизмом
- Хеширование паролей с bcrypt
- Защита от CSRF атак

### 2. Авторизация
- Проверка прав доступа к ресурсам
- Валидация входных данных
- Rate limiting

### 3. Защита данных
- SQL injection protection через ORM
- XSS protection
- CORS настройки

## Масштабируемость

### 1. Горизонтальное масштабирование
- Stateless API сервисы
- Load balancing через Nginx
- Микросервисная архитектура

### 2. Вертикальное масштабирование
- Connection pooling для БД
- Кэширование частых запросов
- Оптимизация запросов

### 3. База данных
- Индексы для быстрых запросов
- Пагинация для больших списков
- Read replicas для чтения

## Мониторинг и логирование

### 1. Логирование
- Структурированные логи
- Уровни логирования (DEBUG, INFO, ERROR)
- Централизованное хранение логов

### 2. Мониторинг
- Health checks для сервисов
- Метрики производительности
- Алерты при проблемах

### 3. Трассировка
- Request ID для отслеживания
- Время выполнения запросов
- Зависимости между сервисами

## Развертывание

### 1. Docker контейнеризация
- Многоконтейнерное приложение
- Изолированные сервисы
- Легкое развертывание

### 2. CI/CD
- Автоматические тесты
- Сборка и деплой
- Rollback механизмы

### 3. Environment Management
- Переменные окружения
- Конфигурация для разных сред
- Секреты управления

## Производительность

### 1. Frontend
- Code splitting
- Lazy loading компонентов
- Оптимизация изображений
- Service Worker для кэширования

### 2. Backend
- Кэширование запросов
- Оптимизация SQL запросов
- Асинхронная обработка
- Connection pooling

### 3. База данных
- Индексы для быстрых запросов
- Query optimization
- Partitioning для больших таблиц

## Тестирование

### 1. Unit Tests
- Тестирование отдельных функций
- Mocking зависимостей
- Покрытие кода

### 2. Integration Tests
- Тестирование API endpoints
- Тестирование взаимодействия компонентов
- Тестирование базы данных

### 3. E2E Tests
- Тестирование пользовательских сценариев
- Автоматизированное тестирование UI
- Тестирование в браузере

## Документация

### 1. API Documentation
- OpenAPI/Swagger спецификация
- Примеры запросов и ответов
- Описание ошибок

### 2. Code Documentation
- Docstrings для функций
- README файлы
- Архитектурная документация

### 3. User Documentation
- Руководство пользователя
- FAQ
- Troubleshooting

## Будущие улучшения

### 1. Функциональность
- Push уведомления
- Real-time чат
- Видео/аудио контент
- AI рекомендации

### 2. Технические улучшения
- GraphQL API
- WebSocket для real-time
- Microservices разбивка
- Kubernetes развертывание

### 3. Масштабирование
- CDN для статических файлов
- Database sharding
- Event-driven архитектура
- Serverless функции
