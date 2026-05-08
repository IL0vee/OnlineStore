# Блог - Веб-приложение

## Описание проекта

**Блог** - это полнофункциональное веб-приложение на Python с использованием Flask для управления блогом. Приложение предоставляет как веб-интерфейс для пользователей, так и REST API для программного доступа.

### Ключевые особенности:
- ✅ Регистрация и аутентификация пользователей
- ✅ Управление постами (CRUD операции)
- ✅ Система комментариев
- ✅ Категории и теги для постов
- ✅ Валидация входных данных (Marshmallow)
- ✅ Логирование действий
- ✅ Полное покрытие тестами (pytest)
- ✅ Готовность к развёртыванию на PythonAnywhere
- ✅ Современный веб-интерфейс с Bootstrap

---

---

## Установка и запуск

### Требования:
- Python 3.8+
- pip

### Шаги установки:

```bash
# 1. Перейти в директорию проекта
cd blog_api

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Инициализировать базу данных
python run.py init-db

# 4. (Опционально) Заполнить БД тестовыми данными
python run.py seed-db

# 5. Запустить приложение
python run.py
```

Приложение будет доступно по адресу: `http://localhost:5000`

---

## Веб-интерфейс

Приложение предоставляет удобный веб-интерфейс для:
- Просмотра постов на главной странице
- Регистрации и входа в систему
- Создания и управления своими постами
- Добавления комментариев к постам
- Фильтрации постов по категориям и тегам

### Основные страницы:
- `/` - Главная страница с последними постами
- `/login` - Вход в систему
- `/register` - Регистрация нового пользователя
- `/create-post` - Создание нового поста
- `/my-posts` - Управление своими постами
- `/post/<id>` - Просмотр конкретного поста
- `/category/<id>` - Посты по категории
- `/tag/<id>` - Посты по тегу

---

## REST API

Приложение также предоставляет REST API для программного доступа. Все API endpoints требуют аутентификации через JWT токен.

### Аутентификация:
- `POST /api/auth/register` - Регистрация
- `POST /api/auth/login` - Вход

### Основные API endpoints:
- `GET /api/posts` - Получить список постов
- `POST /api/posts` - Создать пост
- `GET /api/posts/<id>` - Получить пост
- `PUT /api/posts/<id>` - Обновить пост
- `DELETE /api/posts/<id>` - Удалить пост
- `POST /api/posts/<id>/comments` - Добавить комментарий
- `GET /api/categories` - Получить категории
- `GET /api/tags` - Получить теги

Полную документацию API см. в файле `API_EXAMPLES.md`.

---

```
blog_api/
├── app/
│   ├── __init__.py          # Инициализация Flask
│   ├── models.py            # Модели БД
│   ├── routes.py            # Маршруты API
│   ├── schemas.py           # Схемы валидации Marshmallow
├── logs/                    # Логи приложения
├── migrations/              # Миграции БД (Alembic)
├── .env                     # Переменные окружения
├── requirements.txt         # Зависимости
├── run.py                   # Запуск приложения
├── test_blog_api.py         # Тесты (pytest)
└── README.md               # Этот файл
```

---

## API Endpoints

### Аутентификация

#### Регистрация пользователя
```
POST /api/auth/register
Content-Type: application/json

{
    "username": "newuser",
    "password": "secure_password",
    "full_name": "User Full Name"
}

Response (201):
{
    "message": "User registered successfully",
    "user": {
        "id_user": 1,
        "username": "newuser",
        "full_name": "User Full Name",
        "created_at": "2024-04-10T12:00:00"
    }
}
```

#### Вход пользователя
```
POST /api/auth/login
Content-Type: application/json

{
    "username": "newuser",
    "password": "secure_password"
}

Response (200):
{
    "message": "Login successful",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id_user": 1,
        "username": "newuser",
        "full_name": "User Full Name"
    }
}
```

### Посты (CRUD)

#### Получить все посты
```
GET /api/posts
GET /api/posts?page=1&per_page=10
GET /api/posts?status=published&category_id=1

Response (200):
{
    "posts": [
        {
            "post_id": 1,
            "title": "My First Post",
            "content": "Post content...",
            "status": "published",
            "create_date": "2024-04-10T10:00:00",
            "author": {
                "id_user": 1,
                "username": "author"
            }
        }
    ],
    "total": 10,
    "pages": 1,
    "current_page": 1
}
```

#### Создать пост
```
POST /api/posts
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "title": "My First Post",
    "content": "This is my first blog post content...",
    "id_category": 1,
    "id_tag": 1,
    "status": "published"
}

Response (201):
{
    "message": "Post created",
    "post": {
        "post_id": 1,
        "title": "My First Post",
        ...
    }
}
```

#### Получить пост по ID
```
GET /api/posts/1

Response (200):
{
    "post_id": 1,
    "title": "My First Post",
    "content": "Post content...",
    "comments": [
        {
            "id_comment": 1,
            "text": "Great post!",
            "date": "2024-04-10T11:00:00"
        }
    ]
}
```

#### Обновить пост
```
PUT /api/posts/1
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "title": "Updated Title",
    "content": "Updated content..."
}

Response (200):
{
    "message": "Post updated",
    "post": {...}
}
```

#### Удалить пост
```
DELETE /api/posts/1
Authorization: Bearer {access_token}

Response (200):
{
    "message": "Post deleted"
}
```

### Комментарии

#### Получить комментарии к посту
```
GET /api/posts/1/comments

Response (200):
[
    {
        "id_comment": 1,
        "text": "Great post!",
        "date": "2024-04-10T11:00:00",
        "author": {
            "id_user": 2,
            "username": "reader"
        }
    }
]
```

#### Добавить комментарий
```
POST /api/posts/1/comments
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "text": "This is my comment on the post"
}

Response (201):
{
    "message": "Comment created",
    "comment": {
        "id_comment": 1,
        "text": "This is my comment...",
        "date": "2024-04-10T12:00:00"
    }
}
```

#### Удалить комментарий
```
DELETE /api/comments/1
Authorization: Bearer {access_token}

Response (200):
{
    "message": "Comment deleted"
}
```

### Категории

#### Получить все категории
```
GET /api/categories

Response (200):
[
    {
        "id_category": 1,
        "name": "Technology",
        "created_date": "2024-04-10T10:00:00"
    }
]
```

#### Создать категорию
```
POST /api/categories
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "name": "New Category"
}

Response (201):
{
    "message": "Category created",
    "category": {
        "id_category": 1,
        "name": "New Category"
    }
}
```

### Теги

#### Получить все теги
```
GET /api/tags

Response (200):
[
    {
        "id_tag": 1,
        "name": "python"
    }
]
```

#### Создать тег
```
POST /api/tags
Authorization: Bearer {access_token}
Content-Type: application/json

{
    "name": "newtag"
}

Response (201):
{
    "message": "Tag created",
    "tag": {
        "id_tag": 1,
        "name": "newtag"
    }
}
```

### Поиск и фильтрация

#### Поиск постов
```
GET /api/posts/search?q=python

Response (200):
[
    {
        "post_id": 1,
        "title": "Python Tutorial",
        ...
    }
]
```

#### Посты конкретного автора
```
GET /api/users/1/posts

Response (200):
[
    {
        "post_id": 1,
        "title": "Author's Post",
        ...
    }
]
```

---

## Коды ошибок

| Код | Описание |
|-----|---------|
| 200 | OK - Успешный запрос |
| 201 | Created - Ресурс создан |
| 400 | Bad Request - Неверные данные |
| 401 | Unauthorized - Требуется аутентификация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 409 | Conflict - Ресурс уже существует |
| 500 | Internal Server Error - Ошибка сервера |

---

## Тестирование

### Запуск тестов

```bash
# Запуск всех тестов
pytest test_blog_api.py -v

# Запуск конкретного теста
pytest test_blog_api.py::test_user_registration_success -v

# Запуск с выводом логов
pytest test_blog_api.py -v -s

# Запуск с отчетом о покрытии
pytest test_blog_api.py --cov=app
```

### Покрытие тестами

- ✅ Регистрация и аутентификация (4 теста)
- ✅ CRUD операции для постов (7 тестов)
- ✅ Комментарии (3 теста)
- ✅ Категории и теги (4 теста)
- ✅ Полный workflow (1 тест)

**Всего: 19 тестов**

---

## Логирование

Все действия записываются в файл `logs/blog_api.log`:

```
2024-04-10 10:00:00 INFO: Blog API startup
2024-04-10 10:05:23 INFO: User newuser registered successfully
2024-04-10 10:06:15 INFO: User newuser logged in successfully
2024-04-10 10:07:42 INFO: Post "My First Post" created by user 1
```

---

## Валидация данных

### Username
- Минимум 3 символа
- Максимум 30 символов
- Разрешены: буквы, цифры, подчеркивание

### Пароль
- Минимум 6 символов

### Заголовок поста
- Минимум 3 символа
- Максимум 200 символов

### Содержание поста
- Минимум 10 символов

### Комментарий
- Минимум 1 символ
- Максимум 1000 символов

### Статус поста
- Допустимые значения: `draft`, `published`, `archived`

---

## Развёртывание на PythonAnywhere

### Шаги развёртывания:

1. **Создать аккаунт** на [PythonAnywhere](https://www.pythonanywhere.com)

2. **Загрузить код** либо через Git:
```bash
git clone https://github.com/your-repo/blog_api.git
cd blog_api
```

3. **Создать виртуальное окружение:**
```bash
mkvirtualenv --python=/usr/bin/python3.8 venv
pip install -r requirements.txt
```

4. **Настроить WSGI**:
   - В PythonAnywhere: Web → Add new web app → Manual configuration
   - Редактировать WSGI файл:

```python
import sys
path = '/home/username/blog_api'
if path not in sys.path:
    sys.path.append(path)

from run import app as application
```

5. **Настроить статические файлы** (если нужны):
   - URL: `/static/`
   - Directory: `/home/username/blog_api/static`

6. **Установить переменные окружения** в .env

7. **Перезагрузить приложение**

---

## Примеры использования

### Пример 1: Создание и публикация поста

```bash
# 1. Регистрация
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"blogger","password":"pass123","full_name":"John Blogger"}'

# 2. Вход
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"blogger","password":"pass123"}'

# 3. Создание поста
curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"My Blog Post",
    "content":"This is my first blog post with full content...",
    "status":"published"
  }'
```

### Пример 2: Чтение постов

```bash
# Получить все посты
curl http://localhost:5000/api/posts

# Получить конкретный пост
curl http://localhost:5000/api/posts/1

# Поиск
curl http://localhost:5000/api/posts/search?q=python
```

### Пример 3: Получение JWT токена

```python
import requests

# Регистрация и вход
response = requests.post('http://localhost:5000/api/auth/login', json={
    'username': 'blogger',
    'password': 'pass123'
})

data = response.json()
token = data['access_token']

# Использование токена
headers = {'Authorization': f'Bearer {token}'}
posts_response = requests.post('http://localhost:5000/api/posts',
    headers=headers,
    json={
        'title': 'New Post',
        'content': 'Post content...'
    }
)
```

---

## Структура базы данных

### Users
```sql
CREATE TABLE users (
    id_user INTEGER PRIMARY KEY,
    full_name VARCHAR(150),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Posts
```sql
CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    create_date DATETIME,
    update_date DATETIME,
    id_user INTEGER NOT NULL,
    status VARCHAR(50),
    id_category INTEGER,
    FOREIGN KEY (id_user) REFERENCES users(id_user),
    FOREIGN KEY (id_category) REFERENCES categories(id_category)
);
```

### Comments
```sql
CREATE TABLE comments (
    id_comment INTEGER PRIMARY KEY,
    date DATETIME,
    id_post INTEGER NOT NULL,
    id_user INTEGER NOT NULL,
    text TEXT NOT NULL,
    FOREIGN KEY (id_post) REFERENCES posts(post_id),
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);
```

### Categories
```sql
CREATE TABLE categories (
    id_category INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_date DATETIME
);
```

### Tags
```sql
CREATE TABLE tags (
    id_tag INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
```

### Post-Tags (Many-to-Many)
```sql
CREATE TABLE post_tags (
    post_id INTEGER PRIMARY KEY,
    tag_id INTEGER PRIMARY KEY,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (tag_id) REFERENCES tags(id_tag)
);
```

---

## Обработка ошибок

API возвращает понятные сообщения об ошибках:

```json
{
    "error": "Validation error",
    "messages": {
        "username": ["Username должен быть от 3 до 30 символов"]
    }
}
```

---

## Безопасность

1. **Пароли** хешируются с использованием Werkzeug security
2. **JWT токены** используются для аутентификации
3. **Авторизация** проверяется на каждый защищенный маршрут
4. **CORS** можно настроить при необходимости
5. **SQL инъекции** предотвращены использованием SQLAlchemy ORM
6. **Валидация входных данных** на основе Marshmallow

---

## Решение проблем

### Ошибка "Database is locked"
Убедитесь, что используется правильный драйвер БД и закрыты все соединения.

### Ошибка "Invalid JWT"
Проверьте что токен не истек и был получен правильно

### Ошибка "CORS error"
Добавьте Flask-CORS в requirements.txt и инициализируйте в __init__.py

---

## Лицензия

MIT License

---

## Автор

Проект разработан как учебное задание для демонстрации навыков разработки REST API на Flask.

---

## Контакты

Для вопросов и предложений: [ваш email]

---

**Версия:** 1.0  
**Последнее обновление:** 10 апреля 2024
