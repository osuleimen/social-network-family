# Social Network Platform

Современная платформа социальной сети, разработанная на основе архитектуры Gramps Web API. Позволяет пользователям создавать профили, публиковать посты, просматривать ленту других пользователей и взаимодействовать с контентом.

## 🚀 Быстрый старт

### С Docker (рекомендуется)

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd social_network

# Запустите приложение
./start.sh

# Откройте браузер
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
```

### Без Docker

```bash
# 1. Настройте базу данных PostgreSQL
# 2. Установите зависимости
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 3. Запустите сервисы
# Backend
cd backend && python run.py

# Frontend (в новом терминале)
cd frontend && npm run dev
```

## ✨ Основные возможности

- 👤 **Профили пользователей** - создание и редактирование профилей
- 📝 **Публикация постов** - создание текстовых постов
- 🔄 **Лента новостей** - просмотр постов от подписок
- ❤️ **Лайки и комментарии** - взаимодействие с контентом
- 👥 **Подписки** - подписка на других пользователей
- 🔍 **Поиск** - поиск постов и пользователей
- 🌓 **Темная/светлая тема** - переключение тем оформления
- 📱 **Responsive дизайн** - адаптация под мобильные устройства
- 🏗️ **Интеграция с Gramps** - связывание с генеалогическим деревом

## 🛠️ Технический стек

### Backend
- **Python 3.9+** - основной язык
- **Flask** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Redis** - кэширование
- **JWT** - аутентификация

### Frontend
- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Tailwind CSS** - стилизация
- **React Query** - управление состоянием
- **React Router** - навигация

### DevOps
- **Docker** - контейнеризация
- **Nginx** - веб-сервер
- **Docker Compose** - оркестрация

## 📁 Структура проекта

```
social_network/
├── backend/                 # Flask API
├── frontend/               # React приложение
├── docker-compose.yml      # Docker конфигурация
├── nginx.conf             # Nginx конфигурация
├── start.sh               # Скрипт запуска
└── README.md              # Документация
```

## 🔧 Конфигурация

Скопируйте файл конфигурации:
```bash
cp env.example .env
```

Отредактируйте переменные окружения в `.env` файле.

## 📚 Документация

- [API Documentation](API_DOCUMENTATION.md) - полная документация API
- [Architecture](ARCHITECTURE.md) - описание архитектуры
- [Development](DEVELOPMENT.md) - руководство по разработке
- [Deployment](DEPLOYMENT.md) - инструкции по развертыванию
- [Issues and Solutions](ISSUES_AND_SOLUTIONS.md) - известные проблемы

## 🧪 Тестирование

```bash
# Backend тесты
cd backend && python -m pytest

# Frontend тесты
cd frontend && npm test
```

## 🚀 Развертывание

### Локальное развертывание
```bash
./start.sh
```

### Production развертывание
См. [DEPLOYMENT.md](DEPLOYMENT.md) для подробных инструкций.

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE) для подробностей.

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте [Issues and Solutions](ISSUES_AND_SOLUTIONS.md)
2. Создайте Issue в GitHub
3. Обратитесь к документации

## 🔮 Планы развития

- [ ] Push уведомления
- [ ] Real-time чат
- [ ] Видео/аудио контент
- [ ] AI рекомендации
- [ ] Мобильное приложение
- [ ] GraphQL API
- [ ] WebSocket для real-time функций

---

**Создано с ❤️ на основе архитектуры Gramps Web API**
