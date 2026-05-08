# Быстрый старт - Блог

## ⚡ За 5 минут

### Шаг 1: Клонировать/открыть проект
```bash
cd blog_api
```

### Шаг 2: Установить зависимости
```bash
pip install -r requirements.txt
```

### Шаг 3: Запустить приложение
```bash
python run.py
```

Приложение доступно по адресу: **http://localhost:5000**

---

## 🌐 Использование веб-интерфейса

1. **Регистрация**: Перейдите на `/register` и создайте аккаунт
2. **Вход**: Используйте `/login` для входа
3. **Создание поста**: Нажмите "Создать пост" в меню
4. **Просмотр постов**: Главная страница показывает последние посты
5. **Комментарии**: На странице поста можно оставлять комментарии

---

## 🧪 Запуск тестов

```bash
# Все тесты
pytest -v

# Конкретный тест
pytest test_blog_api.py::test_user_registration_success -v

# С отчетом о покрытии
pytest --cov=app test_blog_api.py
```

---

## 📚 Основные эндпоинты

| Метод | Маршрут | Описание |
|-------|---------|---------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/posts` | Получить посты |
| POST | `/api/posts` | Создать пост |
| PUT | `/api/posts/{id}` | Обновить пост |
| DELETE | `/api/posts/{id}` | Удалить пост |
| POST | `/api/posts/{id}/comments` | Добавить комментарий |
| POST | `/api/categories` | Создать категорию |
| POST | `/api/tags` | Создать тег |

---

## 🔐 Аутентификация

```bash
# 1. Зарегистрироваться
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'

# 2. Получить токен
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'

# 3. Использовать токен
curl http://localhost:5000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📁 Структура проекта

```
blog_api/
├── app/
│   ├── __init__.py       # Инициализация Flask
│   ├── models.py         # БД модели
│   ├── routes.py         # API маршруты
│   └── schemas.py        # Валидация
├── logs/                 # Логи приложения
├── migrations/           # Алембик миграции
├── test_blog_api.py      # Тесты (19 тестов)
├── requirements.txt      # Зависимости
├── run.py               # Запуск
├── .env                 # Конфиг
├── README.md            # Полная документация
├── DEPLOYMENT.md        # Развёртывание
└── API_EXAMPLES.md      # Примеры
```

---

## 🛠️ Вспомогательные команды

```bash
# Инициализировать БД
python run.py init-db

# Заполнить БД тестовыми данными
python run.py seed-db

# Интерактивная оболочка Python
python run.py shell

# Запустить все тесты
pytest -v

# Запустить с логами
pytest -v -s
```

---

## 📊 Завершённые требования

### Задание 1: ER-диаграмма
✅ Модели БД созданы:
- Users, Posts, Comments
- Categories, Tags
- Many-to-Many связь Post-Tags

### Задание 2: Валидация JSON
✅ Marshmallow схемы:
- Проверка username (3-30 символов)
- Проверка пароля (минимум 6 символов)
- Валидация содержимого постов
- Возврат ошибок 400 Bad Request

### Задание 3: Тесты на pytest
✅ 19 автоматических тестов:
- Регистрация и вход
- CRUD операции
- Проверка авторизации
- Валидация ошибок

### Задание 4: Логирование
✅ Запись в файл:
- Кто заходил в систему
- Созданные/удалённые посты
- Ошибки и предупреждения
- Файл: `logs/blog_api.log`

### Задание 5: Аутентификация и авторизация
✅ JWT токены:
- Только автор может редактировать пост
- Только авторизованные могут создавать
- Ошибка 403 за нарушения

### Задание 6: Документация
✅ Несколько документов:
- README.md - полная документация
- DEPLOYMENT.md - развёртывание
- API_EXAMPLES.md - примеры использования
- Этот файл - быстрый старт

### Задание 7: Контейнеризация
✅ Docker файлы:
- Dockerfile для образа
- docker-compose.yml для оркестрации

### Задание 8: Развёртывание
✅ Готов для:
- PythonAnywhere (инструкция в DEPLOYMENT.md)
- Docker контейнеры
- Любой сервер с Python

---

## 🚀 Следующие шаги

### Для развёртывания:
1. Прочитать [DEPLOYMENT.md](./DEPLOYMENT.md)
2. Создать аккаунт на PythonAnywhere
3. Загрузить код
4. Следовать инструкциям

### Для расширения функциональности:
1. Добавить CORS для веб-приложения
2. Реализовать пагинацию (уже есть)
3. Добавить кэширование Redis
4. Добавить WebSocket для real-time комментариев
5. Полнотекстовый поиск

### Для production:
1. Использовать PostgreSQL вместо SQLite
2. Включить HTTPS
3. Настроить Rate Limiting
4. Добавить мониторинг
5. Настроить резервные копии

---

## 🐛 Если что-то не работает

### Ошибка: "No module named 'app'"
```bash
pip install -r requirements.txt
```

### Ошибка: "Database is locked"
```bash
# Удалить старую БД
rm instance/blog.db
python run.py init-db
```

### Тесты не запускаются
```bash
pip install pytest pytest-flask
pytest test_blog_api.py -v
```

### Приложение не запускается
```bash
# Проверить логи
cat logs/blog_api.log

# Проверить синтаксис
python -m py_compile app/__init__.py app/models.py app/routes.py
```

---

## 📖 Дополнительные ресурсы

- **Flask документация**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Marshmallow**: https://marshmallow.readthedocs.io/
- **JWT**: https://tools.ietf.org/html/rfc7519
- **pytest**: https://docs.pytest.org/

---

## 💡 Советы

### Для разработки
```bash
# Использовать debug mode
export FLASK_ENV=development
python run.py

# Использовать интерактивную оболочку
python run.py shell
>>> from app import db
>>> from app.models import User
>>> User.query.all()
```

### Для production
```bash
# Использовать Gunicorn
gunicorn --workers 4 run:app

# Использовать процесс менеджер (supervisor, systemd)
```

---

## 📞 Поддержка и связь

Если возникли вопросы или проблемы:

1. Проверьте [README.md](./README.md) для полной документации
2. Посмотрите [API_EXAMPLES.md](./API_EXAMPLES.md) для примеров
3. Прочитайте [DEPLOYMENT.md](./DEPLOYMENT.md) для развёртывания
4. Проверьте логы в `logs/blog_api.log`

---

## ✨ Version Info

- **Проект**: Блог API
- **Версия**: 1.0
- **Вариант**: 2 - Блог
- **Дата**: 10 апреля 2024
- **Статус**: ✅ Готов к использованию

---

**Спасибо за использование Блог API! Happy coding! 🎉**
