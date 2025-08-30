# Известные проблемы и решения

## Проблемы производительности

### 1. Медленная загрузка ленты постов

**Проблема:** При большом количестве постов лента загружается медленно.

**Причины:**
- N+1 проблема в запросах к базе данных
- Отсутствие пагинации
- Неоптимизированные SQL запросы

**Решения:**
```python
# Оптимизация запросов с eager loading
posts = Post.query.options(
    joinedload('author'),
    joinedload('likes'),
    joinedload('comments')
).filter(
    Post.is_public == True
).order_by(
    Post.created_at.desc()
).paginate(page=page, per_page=20)

# Добавление индексов
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);
```

### 2. Медленная аутентификация

**Проблема:** JWT токены проверяются медленно при каждом запросе.

**Решение:**
```python
# Кэширование проверки токенов
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token_in_redis = redis_client.get(jti)
    return token_in_redis is not None

# Кэширование пользователей
@lru_cache(maxsize=1000)
def get_user_by_id(user_id: int):
    return User.query.get(user_id)
```

### 3. Медленная загрузка изображений

**Проблема:** Аватары пользователей загружаются медленно.

**Решение:**
```typescript
// Lazy loading изображений
const LazyImage = ({ src, alt, ...props }) => {
  const [isLoaded, setIsLoaded] = useState(false);
  
  return (
    <img
      src={isLoaded ? src : '/placeholder.png'}
      alt={alt}
      onLoad={() => setIsLoaded(true)}
      {...props}
    />
  );
};

// Оптимизация изображений
const optimizedImageUrl = (url: string, width: number) => {
  return `${url}?w=${width}&q=80&format=webp`;
};
```

## Проблемы безопасности

### 1. XSS атаки

**Проблема:** Пользовательский контент может содержать вредоносный JavaScript.

**Решение:**
```python
# Backend: Санитизация контента
from bleach import clean

def sanitize_content(content: str) -> str:
    allowed_tags = ['p', 'br', 'strong', 'em', 'u']
    return clean(content, tags=allowed_tags, strip=True)

# Frontend: Использование React для безопасного рендеринга
const PostContent = ({ content }) => {
  return <div dangerouslySetInnerHTML={{ __html: sanitizeHtml(content) }} />;
};
```

### 2. CSRF атаки

**Проблема:** Отсутствие защиты от Cross-Site Request Forgery.

**Решение:**
```python
# Backend: CSRF токены
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

@app.route('/api/posts', methods=['POST'])
@csrf.exempt  # Для API endpoints
def create_post():
    # Валидация токена
    pass

# Frontend: Включение токенов в запросы
const createPost = async (data) => {
  const response = await fetch('/api/posts', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken(),
    },
    body: JSON.stringify(data),
  });
};
```

### 3. SQL Injection

**Проблема:** Небезопасные SQL запросы.

**Решение:**
```python
# Всегда используйте ORM
# Плохо
user = db.execute(f"SELECT * FROM users WHERE username = '{username}'")

# Хорошо
user = User.query.filter_by(username=username).first()

# Для сложных запросов используйте параметризованные запросы
from sqlalchemy import text

query = text("SELECT * FROM users WHERE username = :username")
user = db.session.execute(query, {"username": username}).fetchone()
```

## Проблемы масштабируемости

### 1. Ограничения базы данных

**Проблема:** PostgreSQL не справляется с большим количеством запросов.

**Решение:**
```python
# Connection pooling
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# Read replicas для чтения
READ_DATABASE_URL = "postgresql://readonly:pass@replica:5432/db"

def get_read_db():
    return create_engine(READ_DATABASE_URL)
```

### 2. Ограничения Redis

**Проблема:** Redis память заполняется быстро.

**Решение:**
```python
# Настройка TTL для кэша
redis_client.setex(key, 3600, value)  # TTL 1 час

# Очистка старых данных
def cleanup_old_data():
    # Удаление старых сессий
    old_sessions = redis_client.keys("session:*")
    for session in old_sessions:
        if redis_client.ttl(session) == -1:  # Нет TTL
            redis_client.delete(session)
```

### 3. Ограничения API

**Проблема:** API не справляется с большим количеством запросов.

**Решение:**
```python
# Rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/posts')
@limiter.limit("10 per minute")
def get_posts():
    pass

# Caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_posts(user_id: int):
    return Post.query.filter_by(author_id=user_id).all()
```

## Проблемы пользовательского опыта

### 1. Медленная загрузка страниц

**Проблема:** Страницы загружаются медленно.

**Решение:**
```typescript
// Code splitting
const ProfilePage = lazy(() => import('./pages/ProfilePage'));

// Suspense для загрузки
<Suspense fallback={<LoadingSpinner />}>
  <ProfilePage />
</Suspense>

// Preloading важных страниц
const preloadProfilePage = () => {
  import('./pages/ProfilePage');
};
```

### 2. Плохая обратная связь

**Проблема:** Пользователи не знают о статусе операций.

**Решение:**
```typescript
// Toast уведомления
const { toast } = useToast();

const createPost = async (data) => {
  try {
    toast.loading('Creating post...');
    await api.createPost(data);
    toast.success('Post created successfully!');
  } catch (error) {
    toast.error('Failed to create post');
  }
};

// Skeleton loading
const PostSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
  </div>
);
```

### 3. Проблемы с мобильными устройствами

**Проблема:** Интерфейс плохо работает на мобильных устройствах.

**Решение:**
```css
/* Responsive дизайн */
@media (max-width: 768px) {
  .post-card {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .user-avatar {
    width: 2rem;
    height: 2rem;
  }
}

/* Touch-friendly кнопки */
.btn {
  min-height: 44px;
  min-width: 44px;
  padding: 0.75rem 1rem;
}
```

## Проблемы с данными

### 1. Потеря данных

**Проблема:** Данные могут быть потеряны при сбоях.

**Решение:**
```python
# Транзакции
from contextlib import contextmanager

@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

# Резервное копирование
def backup_database():
    import subprocess
    subprocess.run([
        'pg_dump', '-h', 'localhost', '-U', 'postgres',
        '-d', 'social_network', '-f', f'backup_{datetime.now()}.sql'
    ])
```

### 2. Консистентность данных

**Проблема:** Данные могут стать несогласованными.

**Решение:**
```python
# Валидация на уровне базы данных
class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Ограничения
    __table_args__ = (
        db.CheckConstraint('length(content) > 0', name='content_not_empty'),
    )

# Проверки на уровне приложения
def validate_post_data(data):
    if not data.get('content', '').strip():
        raise ValidationError('Post content cannot be empty')
    
    if len(data['content']) > 1000:
        raise ValidationError('Post content too long')
```

### 3. Дублирование данных

**Проблема:** Одинаковые данные могут быть созданы несколько раз.

**Решение:**
```python
# Уникальные ограничения
class User(db.Model):
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# Проверка перед созданием
def create_user(user_data):
    if User.query.filter_by(username=user_data['username']).first():
        raise ValidationError('Username already exists')
    
    if User.query.filter_by(email=user_data['email']).first():
        raise ValidationError('Email already exists')
    
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    return user
```

## Проблемы интеграции

### 1. Интеграция с Gramps

**Проблема:** Сложность интеграции с генеалогическим деревом.

**Решение:**
```python
# API для работы с Gramps
class GrampsIntegration:
    def __init__(self, gramps_db_path):
        self.db_path = gramps_db_path
    
    def get_person(self, person_id):
        # Логика получения данных из Gramps
        pass
    
    def link_user_to_person(self, user_id, person_id):
        # Связывание пользователя с персоной в Gramps
        pass

# Валидация Gramps данных
def validate_gramps_person(person_id, tree_id):
    try:
        person = gramps_api.get_person(person_id, tree_id)
        return person is not None
    except Exception:
        return False
```

### 2. Интеграция с внешними сервисами

**Проблема:** Зависимость от внешних API.

**Решение:**
```python
# Circuit breaker pattern
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def call_external_api(url, data):
    response = requests.post(url, json=data, timeout=5)
    response.raise_for_status()
    return response.json()

# Fallback механизмы
def get_user_avatar(user_id):
    try:
        return external_avatar_service.get_avatar(user_id)
    except Exception:
        return f'/api/users/{user_id}/avatar'  # Локальный fallback
```

## Проблемы мониторинга

### 1. Отсутствие мониторинга

**Проблема:** Нет возможности отслеживать проблемы в production.

**Решение:**
```python
# Логирование
import structlog

logger = structlog.get_logger()

def create_post(user_id, content):
    logger.info("post_created", 
                user_id=user_id, 
                content_length=len(content))
    
    try:
        post = Post(user_id=user_id, content=content)
        db.session.add(post)
        db.session.commit()
        
        logger.info("post_saved", post_id=post.id)
        return post
    except Exception as e:
        logger.error("post_creation_failed", 
                    user_id=user_id, 
                    error=str(e))
        raise

# Health checks
@app.route('/health')
def health_check():
    try:
        # Проверка базы данных
        db.session.execute('SELECT 1')
        
        # Проверка Redis
        redis_client.ping()
        
        return {'status': 'healthy'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

### 2. Отсутствие метрик

**Проблема:** Нет данных о производительности приложения.

**Решение:**
```python
# Prometheus метрики
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
active_users = Gauge('active_users', 'Number of active users')

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    request_duration.observe(duration)
    request_count.labels(method=request.method, endpoint=request.endpoint).inc()
    return response
```

## Планы по устранению проблем

### Краткосрочные (1-2 недели)
1. Добавить индексы в базу данных
2. Реализовать кэширование
3. Добавить валидацию данных
4. Улучшить обработку ошибок

### Среднесрочные (1-2 месяца)
1. Реализовать пагинацию
2. Добавить rate limiting
3. Улучшить мобильный интерфейс
4. Добавить мониторинг

### Долгосрочные (3-6 месяцев)
1. Микросервисная архитектура
2. Read replicas для базы данных
3. CDN для статических файлов
4. Автоматическое масштабирование

## Полезные инструменты для диагностики

### Backend
- `flask-debugtoolbar` - отладка запросов
- `sqlalchemy-utils` - утилиты для работы с БД
- `memory-profiler` - профилирование памяти
- `line-profiler` - профилирование кода

### Frontend
- React Developer Tools
- Chrome DevTools Performance
- Lighthouse для аудита производительности
- WebPageTest для тестирования скорости

### База данных
- `pg_stat_statements` - статистика запросов
- `pgBadger` - анализ логов PostgreSQL
- `pgAdmin` - GUI для управления БД

### Мониторинг
- Prometheus + Grafana
- Sentry для отслеживания ошибок
- ELK Stack для логов
- New Relic для APM
