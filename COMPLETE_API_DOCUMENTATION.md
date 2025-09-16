# Полная документация API социальной сети GrampsWeb

## Базовый URL
```
http://localhost:5000/api
```

## Аутентификация
API использует JWT токены для аутентификации. Включите токен в заголовок Authorization:
```
Authorization: Bearer <your-access-token>
```

## 1. Аутентификация (Authentication)

### Unified Auth (Унифицированная аутентификация)
- **POST** `/api/unified-auth/request-code` - Запрос кода подтверждения (SMS/Email)
- **POST** `/api/unified-auth/verify-code` - Подтверждение кода
- **POST** `/api/unified-auth/resend-code` - Повторная отправка кода
- **POST** `/api/unified-auth/force-send-code` - Принудительная отправка кода
- **POST** `/api/unified-auth/refresh` - Обновление токена

### SMS Аутентификация
- **POST** `/api/auth/request-code` - Запрос SMS кода
- **POST** `/api/auth/verify-code` - Подтверждение SMS кода
- **POST** `/api/auth/resend-code` - Повторная отправка SMS кода

### Email Аутентификация
- **POST** `/api/auth/email/request-code` - Запрос email кода
- **POST** `/api/auth/email/verify-code` - Подтверждение email кода
- **POST** `/api/auth/email/resend-code` - Повторная отправка email кода

### Google OAuth
- **GET** `/api/auth/google/login` - Авторизация через Google
- **GET** `/api/auth/google/callback` - Callback от Google
- **GET** `/api/auth/google/success` - Успешная авторизация

### Основная аутентификация
- **POST** `/api/auth/refresh` - Обновление access токена
- **GET** `/api/auth/me` - Получение информации о текущем пользователе
- **POST** `/api/auth/logout` - Выход из системы

## 2. Пользователи (Users)

### Профили пользователей
- **GET** `/api/users/profile` - Получение профиля текущего пользователя
- **PUT** `/api/users/profile` - Обновление профиля
- **POST** `/api/users/change-password` - Смена пароля
- **GET** `/api/users/{user_id}` - Получение информации о пользователе
- **GET** `/api/users/by-username/{username}` - Получение пользователя по username
- **GET** `/api/users/by-slug/{profile_slug}` - Получение пользователя по profile_slug

### Управление профилем
- **PUT** `/api/users/profile/username` - Изменение username и profile_slug
- **PUT** `/api/users/profile/avatar` - Загрузка аватара
- **PUT** `/api/users/profile/privacy` - Настройки приватности

## 3. Посты (Posts)

### Основные операции с постами
- **GET** `/api/posts/` - Получение списка постов
- **POST** `/api/posts/` - Создание нового поста
- **GET** `/api/posts/{post_id}` - Получение конкретного поста
- **PUT** `/api/posts/{post_id}` - Обновление поста
- **DELETE** `/api/posts/{post_id}` - Удаление поста
- **POST** `/api/posts/{post_id}/like` - Лайк поста

### Популярная лента
- **GET** `/api/posts/popular` - Получение популярных постов (по лайкам)
- **GET** `/api/posts/popular?window=7d` - Популярные посты за 7 дней
- **GET** `/api/posts/popular?window=30d` - Популярные посты за 30 дней

## 4. Комментарии (Comments)

### Управление комментариями
- **GET** `/api/post/{post_id}/comments` - Получение комментариев к посту
- **POST** `/api/post/{post_id}/comments` - Создание комментария
- **GET** `/api/comments/{comment_id}` - Получение конкретного комментария
- **PUT** `/api/comments/{comment_id}` - Обновление комментария
- **DELETE** `/api/comments/{comment_id}` - Удаление комментария

### Threaded комментарии
- **GET** `/api/comments/{comment_id}/replies` - Получение ответов на комментарий
- **POST** `/api/comments/{comment_id}/replies` - Создание ответа на комментарий

## 5. Медиа файлы (Media)

### Загрузка и управление медиа
- **POST** `/api/posts/{post_id}/media` - Загрузка медиа к посту
- **GET** `/api/posts/{post_id}/media` - Получение медиа поста
- **GET** `/api/media/{media_id}` - Получение информации о медиа файле
- **DELETE** `/api/media/{media_id}` - Удаление медиа файла
- **GET** `/api/media/{media_id}/url` - Получение URL медиа файла
- **GET** `/api/uploads/{filename}` - Получение загруженного файла

### Медиа галерея
- **GET** `/api/users/{user_id}/media` - Получение медиа пользователя
- **GET** `/api/media/{media_id}/variants` - Получение вариантов медиа (thumbnails)

## 6. Подписки (Follows)

### Управление подписками
- **POST** `/api/follow/{user_id}` - Подписка на пользователя
- **POST** `/api/unfollow/{user_id}` - Отписка от пользователя
- **GET** `/api/followers/{user_id}` - Получение списка подписчиков
- **GET** `/api/following/{user_id}` - Получение списка подписок
- **GET** `/api/follow-status/{user_id}` - Проверка статуса подписки
- **GET** `/api/followers-count/{user_id}` - Количество подписчиков
- **GET** `/api/following-count/{user_id}` - Количество подписок

### Запросы на подписку (для приватных аккаунтов)
- **GET** `/api/follow-requests` - Получение входящих запросов на подписку
- **POST** `/api/follow-requests/{request_id}/accept` - Принятие запроса на подписку
- **POST** `/api/follow-requests/{request_id}/decline` - Отклонение запроса на подписку

## 7. Друзья (Friends)

### Управление друзьями
- **POST** `/api/send-request/{user_id}` - Отправка запроса в друзья
- **POST** `/api/accept-request/{request_id}` - Принятие запроса в друзья
- **POST** `/api/decline-request/{request_id}` - Отклонение запроса в друзья
- **POST** `/api/remove-friend/{user_id}` - Удаление из друзей
- **POST** `/api/block-user/{user_id}` - Блокировка пользователя
- **POST** `/api/unblock-user/{user_id}` - Разблокировка пользователя
- **GET** `/api/friends/{user_id}` - Получение списка друзей
- **GET** `/api/pending-requests` - Получение входящих запросов в друзья
- **GET** `/api/sent-requests` - Получение исходящих запросов в друзья
- **GET** `/api/friends-count/{user_id}` - Количество друзей

## 8. Уведомления (Notifications)

### Управление уведомлениями
- **GET** `/api/notifications/` - Получение уведомлений
- **GET** `/api/notifications/unread-count` - Количество непрочитанных уведомлений
- **POST** `/api/notifications/mark-read/{notification_id}` - Отметить уведомление как прочитанное
- **POST** `/api/notifications/mark-all-read` - Отметить все уведомления как прочитанные
- **DELETE** `/api/notifications/delete/{notification_id}` - Удаление уведомления
- **DELETE** `/api/notifications/delete-all` - Удаление всех уведомлений
- **GET** `/api/notifications/types` - Получение типов уведомлений

## 9. Лента (Feed)

### Различные типы лент
- **GET** `/api/feed/home` - Получение домашней ленты
- **GET** `/api/feed/explore` - Получение ленты исследования
- **GET** `/api/feed/friends` - Получение ленты друзей
- **GET** `/api/feed/hashtag/{hashtag}` - Получение постов по хештегу
- **GET** `/api/feed/user/{user_id}` - Получение постов пользователя
- **GET** `/api/feed/popular` - Получение популярной ленты (по лайкам)

## 10. Поиск (Search)

### Поиск по различным критериям
- **GET** `/api/search/users` - Поиск пользователей
- **GET** `/api/search/posts` - Поиск постов
- **GET** `/api/search/hashtags` - Поиск хештегов
- **GET** `/api/search/suggestions` - Поисковые предложения
- **GET** `/api/search/trending` - Трендовые темы

## 11. Администрирование (Admin)

### Управление пользователями
- **GET** `/api/admin/users` - Получение списка пользователей (админ)
- **GET** `/api/admin/users/{user_id}` - Получение информации о пользователе (админ)
- **POST** `/api/admin/users/{user_id}/ban` - Блокировка пользователя (админ)
- **POST** `/api/admin/users/{user_id}/unban` - Разблокировка пользователя (админ)
- **PUT** `/api/admin/users/{user_id}/role` - Изменение роли пользователя (админ)
- **POST** `/api/admin/users/{user_id}/impersonate` - Имперсонация пользователя (SuperAdmin)

### Управление контентом
- **GET** `/api/admin/posts` - Получение всех постов (админ)
- **DELETE** `/api/admin/posts/{post_id}/delete` - Удаление поста (админ)
- **DELETE** `/api/admin/comments/{comment_id}/delete` - Удаление комментария (админ)

### Статистика и мониторинг
- **GET** `/api/admin/stats` - Статистика системы (админ)
- **GET** `/api/admin/recent-activity` - Последняя активность (админ)
- **GET** `/api/admin/audit-logs` - Логи аудита (админ)

## 12. Модерация и жалобы (Reports)

### Система жалоб
- **POST** `/api/reports` - Создание жалобы
- **GET** `/api/reports` - Получение жалоб (модератор)
- **GET** `/api/reports/{report_id}` - Получение конкретной жалобы
- **PUT** `/api/reports/{report_id}/assign` - Назначение модератора
- **PUT** `/api/reports/{report_id}/resolve` - Решение жалобы
- **PUT** `/api/reports/{report_id}/reject` - Отклонение жалобы

### AI модерация
- **POST** `/api/moderation/analyze` - AI анализ контента
- **GET** `/api/moderation/flags` - Получение флагов модерации

## 13. Искусственный интеллект (AI)

### AI помощник
- **POST** `/api/ai/generate-description` - Генерация описания
- **POST** `/api/ai/generate-hashtags` - Генерация хештегов
- **POST** `/api/ai/enhance-content` - Улучшение контента
- **POST** `/api/ai/auto-generate-post` - Автоматическая генерация поста
- **POST** `/api/ai/generate-image` - Генерация изображения
- **GET** `/api/ai/status` - Статус AI сервиса
- **GET** `/api/ai/languages` - Поддерживаемые языки

## 14. Статические файлы
- **GET** `/uploads/{filename}` - Получение загруженных файлов

## Особенности API:

### 1. Аутентификация
- Используется JWT токены с заголовком `Authorization: Bearer <token>`
- Поддержка refresh токенов
- Множественные методы аутентификации (SMS, Email, Google OAuth)

### 2. CORS
- Настроен для работы с фронтендом
- Поддерживает все основные HTTP методы
- Обработка preflight запросов

### 3. Rate Limiting
- Ограничение на количество запросов кода подтверждения (3 запроса в минуту)
- Защита от брутфорс атак

### 4. Медиа файлы
- Интеграция с Gramps Web API для хранения медиа файлов
- Поддержка различных форматов (JPEG, PNG, GIF, WebP)
- Автоматическая генерация thumbnails

### 5. Многоязычность
- Поддержка казахского, английского и русского языков
- AI подсказки на разных языках

### 6. Типы аутентификации
- SMS (только для тестового номера +7 701 999 04 38)
- Email
- Google OAuth
- Унифицированная аутентификация (автоматическое определение типа)

### 7. Пагинация
- Большинство эндпоинтов поддерживают параметры `page` и `per_page`
- Cursor-based пагинация для лент

### 8. Поиск и фильтрация
- Поддержка поиска по различным критериям
- Full-text search для постов и пользователей
- Трендовые хештеги

### 9. RBAC (Role-Based Access Control)
- SuperAdmin: полный доступ, создание админов, имперсонация
- Admin: управление пользователями, статистика, назначение модераторов
- Moderator: модерация контента, обработка жалоб
- User: обычный пользователь

### 10. PII защита
- DOB и Gramps ID видны только владельцу и администраторам
- Логирование доступа к PII
- Шифрование чувствительных данных

### 11. Audit Logging
- Все административные действия логируются
- Отслеживание изменений ролей и статусов
- Логирование имперсонации

### 12. Follow vs Friend логика
- Follow: асимметрично, поддержка приватных аккаунтов
- Friend: взаимно, требует подтверждения
- Автоматическое создание mutual follows при принятии friend request

### 13. Популярная лента
- Алгоритм по лайкам с tie-breaker по времени
- Поддержка временных окон (7d, 30d, all time)
- Materialized views для производительности

### 14. AI интеграция
- Gemini для подсказок и модерации
- Human-in-the-loop подход
- Rate limiting для AI запросов
- Кэширование AI предложений

Все API эндпоинты работают через nginx reverse proxy и доступны по базовому URL с префиксом `/api/`.

