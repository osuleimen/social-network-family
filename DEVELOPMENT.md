# Руководство по разработке

## Настройка среды разработки

### Предварительные требования

1. **Python 3.9+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.9 python3.9-venv python3.9-dev
   
   # macOS
   brew install python@3.9
   
   # Windows
   # Скачайте с python.org
   ```

2. **Node.js 18+**
   ```bash
   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # macOS
   brew install node@18
   
   # Windows
   # Скачайте с nodejs.org
   ```

3. **PostgreSQL 15+**
   ```bash
   # Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql@15
   
   # Windows
   # Скачайте с postgresql.org
   ```

4. **Redis**
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   
   # macOS
   brew install redis
   
   # Windows
   # Скачайте с redis.io
   ```

5. **Git**
   ```bash
   # Ubuntu/Debian
   sudo apt install git
   
   # macOS
   brew install git
   
   # Windows
   # Скачайте с git-scm.com
   ```

### Настройка проекта

1. **Клонирование репозитория**
   ```bash
   git clone <repository-url>
   cd social_network
   ```

2. **Настройка переменных окружения**
   ```bash
   cp env.example .env
   # Отредактируйте .env файл
   ```

3. **Настройка базы данных**
   ```bash
   # Создайте базу данных
   sudo -u postgres psql
   CREATE DATABASE social_network;
   CREATE USER social_user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE social_network TO social_user;
   \q
   ```

4. **Настройка бэкенда**
   ```bash
   cd backend
   
   # Создайте виртуальное окружение
   python3.9 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # venv\Scripts\activate  # Windows
   
   # Установите зависимости
   pip install -r requirements.txt
   
   # Инициализируйте базу данных
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Настройка фронтенда**
   ```bash
   cd frontend
   
   # Установите зависимости
   npm install
   ```

## Запуск в режиме разработки

### Запуск бэкенда

```bash
cd backend
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Запуск Flask сервера
flask run --debug
```

### Запуск фронтенда

```bash
cd frontend

# Запуск dev сервера
npm run dev
```

### Запуск Redis

```bash
# Ubuntu/Debian
sudo systemctl start redis-server

# macOS
brew services start redis

# Windows
redis-server
```

## Структура проекта

```
social_network/
├── backend/                 # Flask API
│   ├── app/
│   │   ├── models/         # Модели данных
│   │   ├── api/            # API endpoints
│   │   ├── auth/           # Аутентификация
│   │   └── utils/          # Утилиты
│   ├── migrations/         # Миграции БД
│   ├── tests/             # Тесты
│   ├── requirements.txt    # Python зависимости
│   └── run.py             # Точка входа
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   ├── pages/          # Страницы
│   │   ├── contexts/       # React контексты
│   │   ├── hooks/          # Кастомные хуки
│   │   ├── services/       # API сервисы
│   │   ├── types/          # TypeScript типы
│   │   └── utils/          # Утилиты
│   ├── public/             # Статические файлы
│   └── package.json        # Node.js зависимости
├── docker-compose.yml      # Docker конфигурация
├── nginx.conf             # Nginx конфигурация
└── README.md              # Документация
```

## Конвенции кодирования

### Python (Backend)

1. **PEP 8 стиль**
   ```python
   # Хорошо
   def create_user(user_data: dict) -> User:
       """Create a new user."""
       user = User(**user_data)
       db.session.add(user)
       db.session.commit()
       return user
   
   # Плохо
   def createUser(userData):
       user=User(**userData)
       db.session.add(user)
       db.session.commit()
       return user
   ```

2. **Типизация**
   ```python
   from typing import List, Optional, Dict
   
   def get_users(page: int = 1, per_page: int = 20) -> Dict[str, any]:
       """Get paginated users."""
       pass
   ```

3. **Docstrings**
   ```python
   def register_user(user_data: dict) -> User:
       """
       Register a new user.
       
       Args:
           user_data: User registration data
           
       Returns:
           User: Created user object
           
       Raises:
           ValidationError: If user data is invalid
       """
       pass
   ```

### TypeScript (Frontend)

1. **Стиль кода**
   ```typescript
   // Хорошо
   interface User {
     id: number;
     username: string;
     email: string;
   }
   
   const createUser = async (userData: User): Promise<User> => {
     const response = await api.post('/users', userData);
     return response.data;
   };
   
   // Плохо
   const createUser = async (userData) => {
     const response = await api.post('/users', userData);
     return response.data;
   };
   ```

2. **Компоненты**
   ```typescript
   interface UserCardProps {
     user: User;
     onFollow?: (userId: number) => void;
   }
   
   const UserCard: React.FC<UserCardProps> = ({ user, onFollow }) => {
     return (
       <div className="user-card">
         <h3>{user.username}</h3>
         {onFollow && (
           <button onClick={() => onFollow(user.id)}>
             Follow
           </button>
         )}
       </div>
     );
   };
   ```

3. **Хуки**
   ```typescript
   const useUser = (userId: number) => {
     const { data, isLoading, error } = useQuery({
       queryKey: ['user', userId],
       queryFn: () => apiClient.getUser(userId),
     });
   
     return { user: data?.user, isLoading, error };
   };
   ```

## Тестирование

### Backend тесты

1. **Unit тесты**
   ```bash
   cd backend
   python -m pytest tests/unit/ -v
   ```

2. **Integration тесты**
   ```bash
   python -m pytest tests/integration/ -v
   ```

3. **API тесты**
   ```bash
   python -m pytest tests/api/ -v
   ```

### Frontend тесты

1. **Unit тесты**
   ```bash
   cd frontend
   npm test
   ```

2. **E2E тесты**
   ```bash
   npm run test:e2e
   ```

### Примеры тестов

**Backend (pytest)**
```python
import pytest
from app.models import User
from app import db

def test_create_user():
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    user = User(**user_data)
    db.session.add(user)
    db.session.commit()
    
    assert user.id is not None
    assert user.username == 'testuser'
```

**Frontend (Jest + React Testing Library)**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginPage from '../pages/LoginPage';

const queryClient = new QueryClient();

test('renders login form', () => {
  render(
    <QueryClientProvider client={queryClient}>
      <LoginPage />
    </QueryClientProvider>
  );
  
  expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
});
```

## Git workflow

### Ветки

- `main` - основная ветка, стабильный код
- `develop` - ветка разработки
- `feature/*` - новые функции
- `bugfix/*` - исправления багов
- `hotfix/*` - срочные исправления

### Commit сообщения

```
type(scope): description

feat(auth): add JWT authentication
fix(api): resolve user creation bug
docs(readme): update installation instructions
style(components): fix indentation
refactor(services): extract API client logic
test(users): add unit tests for user model
```

### Pull Request процесс

1. Создайте ветку от `develop`
2. Внесите изменения
3. Напишите тесты
4. Обновите документацию
5. Создайте Pull Request
6. Пройдите code review
7. Merge в `develop`

## Отладка

### Backend отладка

1. **Логирование**
   ```python
   import logging
   
   logging.basicConfig(level=logging.DEBUG)
   logger = logging.getLogger(__name__)
   
   logger.debug('Debug message')
   logger.info('Info message')
   logger.error('Error message')
   ```

2. **Отладчик**
   ```python
   import pdb
   
   def some_function():
       pdb.set_trace()  # Точка останова
       # код
   ```

3. **Flask debug режим**
   ```bash
   export FLASK_ENV=development
   export FLASK_DEBUG=1
   flask run
   ```

### Frontend отладка

1. **React Developer Tools**
   - Установите расширение для браузера
   - Используйте для отладки компонентов

2. **Redux DevTools** (если используется Redux)
   - Установите расширение
   - Отслеживайте состояние приложения

3. **Console logging**
   ```typescript
   console.log('Debug info:', data);
   console.error('Error:', error);
   console.warn('Warning:', warning);
   ```

## Производительность

### Backend оптимизация

1. **Database queries**
   ```python
   # Плохо - N+1 проблема
   users = User.query.all()
   for user in users:
       print(user.posts.count())
   
   # Хорошо - eager loading
   users = User.query.options(joinedload('posts')).all()
   for user in users:
       print(len(user.posts))
   ```

2. **Кэширование**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_user_stats(user_id: int):
       return User.query.get(user_id).posts.count()
   ```

### Frontend оптимизация

1. **React.memo для компонентов**
   ```typescript
   const UserCard = React.memo(({ user }: UserCardProps) => {
     return <div>{user.name}</div>;
   });
   ```

2. **useMemo для вычислений**
   ```typescript
   const expensiveValue = useMemo(() => {
     return heavyComputation(data);
   }, [data]);
   ```

3. **useCallback для функций**
   ```typescript
   const handleClick = useCallback(() => {
     // обработка клика
   }, []);
   ```

## Безопасность

### Backend безопасность

1. **Валидация входных данных**
   ```python
   from marshmallow import Schema, fields, validate
   
   class UserSchema(Schema):
       username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
       email = fields.Email(required=True)
       password = fields.Str(required=True, validate=validate.Length(min=6))
   ```

2. **SQL injection protection**
   ```python
   # Хорошо - используйте ORM
   user = User.query.filter_by(username=username).first()
   
   # Плохо - raw SQL
   user = db.execute(f"SELECT * FROM users WHERE username = '{username}'")
   ```

### Frontend безопасность

1. **XSS protection**
   ```typescript
   // Хорошо - используйте React
   <div>{userInput}</div>
   
   // Плохо - innerHTML
   element.innerHTML = userInput;
   ```

2. **CSRF protection**
   ```typescript
   // Включите CSRF токены в запросы
   const response = await fetch('/api/posts', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'X-CSRF-Token': csrfToken,
     },
     body: JSON.stringify(data),
   });
   ```

## Развертывание

### Staging environment

1. **Настройка staging**
   ```bash
   # Создайте staging ветку
   git checkout -b staging
   
   # Настройте переменные окружения
   cp env.example .env.staging
   # Отредактируйте .env.staging
   ```

2. **Деплой на staging**
   ```bash
   # Соберите и запустите
   docker-compose -f docker-compose.staging.yml up --build
   ```

### Production deployment

1. **Подготовка к production**
   ```bash
   # Создайте production ветку
   git checkout -b production
   
   # Настройте production переменные
   cp env.example .env.production
   # Отредактируйте .env.production
   ```

2. **Деплой**
   ```bash
   # Соберите production образы
   docker-compose -f docker-compose.prod.yml build
   
   # Запустите production
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Мониторинг

### Логирование

1. **Structured logging**
   ```python
   import structlog
   
   logger = structlog.get_logger()
   
   logger.info("user_registered", 
               user_id=user.id, 
               username=user.username)
   ```

2. **Error tracking**
   ```python
   import sentry_sdk
   
   sentry_sdk.init(dsn="your-sentry-dsn")
   
   try:
       # код
   except Exception as e:
       sentry_sdk.capture_exception(e)
   ```

### Метрики

1. **Prometheus метрики**
   ```python
   from prometheus_client import Counter, Histogram
   
   request_count = Counter('http_requests_total', 'Total HTTP requests')
   request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
   
   @request_duration.time()
   def api_endpoint():
       request_count.inc()
       # код
   ```

## Полезные команды

### Backend

```bash
# Запуск тестов
python -m pytest

# Создание миграции
flask db migrate -m "Description"

# Применение миграций
flask db upgrade

# Откат миграции
flask db downgrade

# Создание суперпользователя
flask create-admin

# Очистка кэша
flask cache clear
```

### Frontend

```bash
# Запуск dev сервера
npm run dev

# Сборка для production
npm run build

# Запуск тестов
npm test

# Проверка типов
npm run type-check

# Линтинг
npm run lint

# Форматирование кода
npm run format
```

### Docker

```bash
# Сборка образов
docker-compose build

# Запуск сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down

# Очистка
docker system prune -a
```

## Ресурсы

### Документация

- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

### Инструменты

- [Postman](https://www.postman.com/) - API тестирование
- [Insomnia](https://insomnia.rest/) - API клиент
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL GUI
- [Redis Commander](https://github.com/joeferner/redis-commander) - Redis GUI

### Полезные расширения VS Code

- Python
- TypeScript and JavaScript Language Features
- Tailwind CSS IntelliSense
- GitLens
- Docker
- REST Client
