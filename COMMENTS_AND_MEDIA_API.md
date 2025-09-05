# API для комментариев и медиа файлов

## Новые API endpoints

### Комментарии

#### Получить комментарии к посту
```http
GET /api/post/{post_id}/comments
```

#### Создать комментарий
```http
POST /api/post/{post_id}/comments
Content-Type: application/json

{
  "content": "Текст комментария"
}
```

#### Обновить комментарий
```http
PUT /api/comments/{comment_id}
Content-Type: application/json

{
  "content": "Обновленный текст"
}
```

#### Удалить комментарий
```http
DELETE /api/comments/{comment_id}
```

### Медиа файлы

#### Загрузить медиа к посту
```http
POST /api/posts/{post_id}/media
Content-Type: multipart/form-data

files: File[]
```

Поддерживаемые форматы: JPEG, PNG, GIF, WebP
Максимальный размер файла: 10MB
Максимальное количество файлов: 10

#### Получить медиа поста
```http
GET /api/posts/{post_id}/media
```

#### Удалить медиа файл
```http
DELETE /api/media/{media_id}
```

#### Получить URL медиа файла
```http
GET /api/media/{media_id}/url
```

## Интеграция с Gramps Web API

Медиа файлы сохраняются в Gramps Web API и доступны по следующей схеме:
- Файлы загружаются в Gramps через `/api/media/` endpoint
- Получается `gramps_media_id` и `gramps_url`
- URL для доступа: `{GRAMPS_BASE_URL}/api/media/{gramps_media_id}/file`

## Переменные окружения

Добавлены новые переменные для интеграции с Gramps:

```env
GRAMPS_BASE_URL=http://grampsweb:5000
GRAMPS_API_KEY=your_api_key_here
```

## Модели данных

### Comment
```python
{
  "id": int,
  "content": str,
  "author_id": int,
  "post_id": int,
  "created_at": datetime,
  "updated_at": datetime,
  "author": User
}
```

### Media
```python
{
  "id": int,
  "filename": str,
  "original_filename": str,
  "mime_type": str,
  "file_size": int,
  "gramps_media_id": str,
  "gramps_url": str,
  "post_id": int,
  "uploaded_by": int,
  "created_at": datetime,
  "uploader": User
}
```

## Обновления в Post модели

Модель Post теперь включает:
- `comments`: список комментариев
- `media`: список медиа файлов
- `comments_count`: количество комментариев
- `media_count`: количество медиа файлов (вычисляется)

## Frontend компоненты

### CommentsSection
Компонент для отображения и управления комментариями к посту:
- Добавление нового комментария
- Отображение списка комментариев
- Редактирование и удаление собственных комментариев

### MediaGallery  
Компонент для отображения медиа файлов:
- Адаптивная сетка для разного количества изображений
- Модальное окно для просмотра
- Возможность удаления (для владельца)

### MediaUpload
Компонент для загрузки медиа файлов:
- Drag & drop поддержка
- Превью перед загрузкой
- Валидация файлов
- Прогресс загрузки

## Обновления существующих компонентов

### PostCard
- Добавлено отображение медиа галереи
- Интегрирована секция комментариев
- Добавлена возможность загружать медиа к существующим постам

### CreatePostForm
- Добавлена возможность прикреплять медиа при создании поста
- Превью выбранных файлов

## Использование

1. При создании поста теперь можно сразу прикрепить изображения
2. К существующим постам можно добавлять изображения через меню поста
3. Комментарии отображаются при клике на счетчик комментариев
4. Медиа файлы отображаются в виде адаптивной галереи
5. Все операции с комментариями и медиа требуют аутентификации
