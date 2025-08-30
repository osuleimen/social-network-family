# API Документация

## Базовый URL

```
http://localhost:5000/api
```

## Аутентификация

API использует JWT токены для аутентификации. Включите токен в заголовок Authorization:

```
Authorization: Bearer <your-access-token>
```

## Endpoints

### Аутентификация

#### POST /auth/register

Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Optional bio",
  "gramps_person_id": "optional-person-id",
  "gramps_tree_id": "optional-tree-id"
}
```

**Ответ:**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Optional bio",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST /auth/login

Вход в систему.

**Тело запроса:**
```json
{
  "username": "johndoe",
  "password": "password123"
}
```

**Ответ:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /auth/refresh

Обновление access токена.

**Заголовки:**
```
Authorization: Bearer <refresh-token>
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### GET /auth/me

Получение информации о текущем пользователе.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Optional bio",
    "followers_count": 5,
    "following_count": 3,
    "posts_count": 10
  }
}
```

#### POST /auth/logout

Выход из системы.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Logout successful"
}
```

### Пользователи

#### GET /users

Получение списка пользователей.

**Параметры запроса:**
- `page` (int): Номер страницы (по умолчанию: 1)
- `per_page` (int): Количество пользователей на странице (по умолчанию: 20)
- `search` (string): Поисковый запрос

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "followers_count": 5,
      "following_count": 3,
      "posts_count": 10
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1
}
```

#### GET /users/{user_id}

Получение информации о конкретном пользователе.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Optional bio",
    "followers_count": 5,
    "following_count": 3,
    "posts_count": 10,
    "is_following": true
  }
}
```

#### PUT /users/me

Обновление профиля текущего пользователя.

**Тело запроса:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "bio": "Updated bio"
  }
}
```

#### POST /users/{user_id}/follow

Подписка на пользователя.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Successfully followed user"
}
```

#### POST /users/{user_id}/unfollow

Отписка от пользователя.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Successfully unfollowed user"
}
```

#### GET /users/{user_id}/followers

Получение списка подписчиков пользователя.

**Параметры запроса:**
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "followers": [
    {
      "id": 2,
      "username": "janedoe",
      "first_name": "Jane",
      "last_name": "Doe"
    }
  ],
  "total": 5,
  "pages": 1,
  "current_page": 1
}
```

#### GET /users/{user_id}/following

Получение списка пользователей, на которых подписан пользователь.

**Параметры запроса:**
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "following": [
    {
      "id": 3,
      "username": "bobsmith",
      "first_name": "Bob",
      "last_name": "Smith"
    }
  ],
  "total": 3,
  "pages": 1,
  "current_page": 1
}
```

### Посты

#### POST /posts

Создание нового поста.

**Тело запроса:**
```json
{
  "content": "Hello, world!",
  "is_public": true
}
```

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Post created successfully",
  "post": {
    "id": 1,
    "content": "Hello, world!",
    "is_public": true,
    "created_at": "2024-01-01T00:00:00Z",
    "author": {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "likes_count": 0,
    "comments_count": 0
  }
}
```

#### GET /posts/{post_id}

Получение конкретного поста.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "post": {
    "id": 1,
    "content": "Hello, world!",
    "is_public": true,
    "created_at": "2024-01-01T00:00:00Z",
    "author": {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "likes_count": 5,
    "comments_count": 2
  }
}
```

#### PUT /posts/{post_id}

Обновление поста.

**Тело запроса:**
```json
{
  "content": "Updated content",
  "is_public": false
}
```

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Post updated successfully",
  "post": {
    "id": 1,
    "content": "Updated content",
    "is_public": false
  }
}
```

#### DELETE /posts/{post_id}

Удаление поста.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Post deleted successfully"
}
```

#### POST /posts/{post_id}/like

Лайк поста.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Post liked successfully"
}
```

#### POST /posts/{post_id}/unlike

Удаление лайка с поста.

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Post unliked successfully"
}
```

#### POST /posts/{post_id}/comments

Создание комментария к посту.

**Тело запроса:**
```json
{
  "content": "Great post!",
  "parent_id": null
}
```

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "message": "Comment created successfully",
  "comment": {
    "id": 1,
    "content": "Great post!",
    "post_id": 1,
    "parent_id": null,
    "created_at": "2024-01-01T00:00:00Z",
    "author": {
      "id": 2,
      "username": "janedoe",
      "first_name": "Jane",
      "last_name": "Doe"
    },
    "replies_count": 0
  }
}
```

#### GET /posts/{post_id}/comments

Получение комментариев к посту.

**Параметры запроса:**
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "comments": [
    {
      "id": 1,
      "content": "Great post!",
      "post_id": 1,
      "parent_id": null,
      "created_at": "2024-01-01T00:00:00Z",
      "author": {
        "id": 2,
        "username": "janedoe",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "replies_count": 1
    }
  ],
  "total": 5,
  "pages": 1,
  "current_page": 1
}
```

### Лента

#### GET /feed

Получение ленты постов (посты от подписок и собственные посты).

**Параметры запроса:**
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "posts": [
    {
      "id": 1,
      "content": "Hello, world!",
      "created_at": "2024-01-01T00:00:00Z",
      "author": {
        "id": 1,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "likes_count": 5,
      "comments_count": 2
    }
  ],
  "total": 50,
  "pages": 5,
  "current_page": 1
}
```

#### GET /feed/explore

Получение ленты исследования (все публичные посты).

**Параметры запроса:**
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "posts": [
    {
      "id": 1,
      "content": "Hello, world!",
      "created_at": "2024-01-01T00:00:00Z",
      "author": {
        "id": 1,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "likes_count": 5,
      "comments_count": 2
    }
  ],
  "total": 100,
  "pages": 10,
  "current_page": 1
}
```

#### GET /feed/search

Поиск постов по содержимому.

**Параметры запроса:**
- `q` (string): Поисковый запрос (обязательный)
- `page` (int): Номер страницы
- `per_page` (int): Количество на странице

**Заголовки:**
```
Authorization: Bearer <access-token>
```

**Ответ:**
```json
{
  "posts": [
    {
      "id": 1,
      "content": "Hello, world!",
      "created_at": "2024-01-01T00:00:00Z",
      "author": {
        "id": 1,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "likes_count": 5,
      "comments_count": 2
    }
  ],
  "total": 10,
  "pages": 1,
  "current_page": 1,
  "query": "hello"
}
```

## Коды ошибок

### HTTP статус коды

- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

### Формат ошибок

```json
{
  "error": "Error message",
  "details": {
    "field": "Specific field error"
  }
}
```

## Примеры использования

### JavaScript (Fetch)

```javascript
// Регистрация
const register = async (userData) => {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  return response.json();
};

// Создание поста
const createPost = async (content, token) => {
  const response = await fetch('/api/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ content, is_public: true }),
  });
  return response.json();
};

// Получение ленты
const getFeed = async (token, page = 1) => {
  const response = await fetch(`/api/feed?page=${page}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return response.json();
};
```

### Python (Requests)

```python
import requests

# Регистрация
def register(user_data):
    response = requests.post(
        'http://localhost:5000/api/auth/register',
        json=user_data
    )
    return response.json()

# Создание поста
def create_post(content, token):
    response = requests.post(
        'http://localhost:5000/api/posts',
        headers={'Authorization': f'Bearer {token}'},
        json={'content': content, 'is_public': True}
    )
    return response.json()

# Получение ленты
def get_feed(token, page=1):
    response = requests.get(
        f'http://localhost:5000/api/feed?page={page}',
        headers={'Authorization': f'Bearer {token}'}
    )
    return response.json()
```

### cURL

```bash
# Регистрация
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Создание поста
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "Hello, world!",
    "is_public": true
  }'

# Получение ленты
curl -X GET http://localhost:5000/api/feed \
  -H "Authorization: Bearer YOUR_TOKEN"
```
