# Примеры использования Блог API

Этот документ содержит практические примеры использования API с помощью различных инструментов и языков программирования.

## Содержание

1. [cURL примеры](#curl-примеры)
2. [Python примеры](#python-примеры)
3. [JavaScript/Node.js примеры](#javascriptnodejs-примеры)
4. [Postman коллекция](#postman-коллекция)
5. [Частые сценарии](#частые-сценарии)

---

## cURL примеры

### 1. Регистрация пользователя

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securePassword123",
    "full_name": "John Doe"
  }'
```

**Ответ (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id_user": 1,
    "username": "john_doe",
    "full_name": "John Doe",
    "created_at": "2024-04-10T12:00:00"
  }
}
```

### 2. Вход пользователя

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securePassword123"
  }'
```

**Ответ (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id_user": 1,
    "username": "john_doe"
  }
}
```

### 3. Создание поста

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Best Practices",
    "content": "In this post, I will share some Python best practices that every developer should know...",
    "status": "published"
  }'
```

### 4. Получение всех постов

```bash
curl http://localhost:5000/api/posts
```

### 5. Получение конкретного поста

```bash
curl http://localhost:5000/api/posts/1
```

### 6. Обновление поста

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X PUT http://localhost:5000/api/posts/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "Updated content..."
  }'
```

### 7. Удаление поста

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X DELETE http://localhost:5000/api/posts/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Добавление комментария

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST http://localhost:5000/api/posts/1/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Great article! Very helpful."
  }'
```

### 9. Получение комментариев к посту

```bash
curl http://localhost:5000/api/posts/1/comments
```

### 10. Поиск постов

```bash
curl "http://localhost:5000/api/posts/search?q=python"
```

---

## Python примеры

### Базовая установка

```python
import requests

BASE_URL = "http://localhost:5000"

# Создать сессию с дефолтными заголовками
session = requests.Session()
```

### Пример 1: Регистрация и вход

```python
import requests

BASE_URL = "http://localhost:5000"

# Регистрация
register_response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": "python_user",
        "password": "securePass123",
        "full_name": "Python User"
    }
)

print(f"Registration: {register_response.status_code}")
print(register_response.json())

# Вход
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "username": "python_user",
        "password": "securePass123"
    }
)

token = login_response.json()["access_token"]
print(f"Token: {token}")
```

### Пример 2: Управление постами

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "your_access_token_here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Создание поста
post_data = {
    "title": "My First Blog Post",
    "content": "This is my first blog post with Python API client",
    "status": "published"
}

post_response = requests.post(
    f"{BASE_URL}/api/posts",
    json=post_data,
    headers=headers
)

post_id = post_response.json()["post"]["post_id"]
print(f"Created post with ID: {post_id}")

# Получение всех постов
all_posts = requests.get(f"{BASE_URL}/api/posts")
for post in all_posts.json()["posts"]:
    print(f"- {post['title']} by {post['author']['username']}")

# Получение конкретного поста
specific_post = requests.get(f"{BASE_URL}/api/posts/{post_id}")
print(specific_post.json())

# Обновление поста
update_data = {
    "title": "Updated Title",
    "content": "Updated content with more information"
}

update_response = requests.put(
    f"{BASE_URL}/api/posts/{post_id}",
    json=update_data,
    headers=headers
)

print(f"Update status: {update_response.status_code}")

# Удаление поста
delete_response = requests.delete(
    f"{BASE_URL}/api/posts/{post_id}",
    headers=headers
)

print(f"Delete status: {delete_response.status_code}")
```

### Пример 3: Управление комментариями

```python
import requests

BASE_URL = "http://localhost:5000"
TOKEN = "your_access_token_here"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Добавление комментария
comment_data = {
    "text": "This is a great post! Thanks for sharing."
}

comment_response = requests.post(
    f"{BASE_URL}/api/posts/1/comments",
    json=comment_data,
    headers=headers
)

print(f"Comment added: {comment_response.json()}")

# Получение комментариев
comments = requests.get(f"{BASE_URL}/api/posts/1/comments")
for comment in comments.json():
    print(f"Comment by {comment['author']['username']}: {comment['text']}")

# Удаление комментария
delete_response = requests.delete(
    f"{BASE_URL}/api/comments/1",
    headers=headers
)

print(f"Delete comment status: {delete_response.status_code}")
```

### Пример 4: Обработка ошибок

```python
import requests

BASE_URL = "http://localhost:5000"

def api_request(method, endpoint, **kwargs):
    \"\"\"Вспомогательная функция для API запросов с обработкой ошибок\"\"\"
    
    url = f"{BASE_URL}/{endpoint}"
    
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()  # Вызвать исключение для плохих статус кодов
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("Error: Unauthorized - Check your token")
        elif response.status_code == 400:
            print(f"Error: Bad Request - {response.json()['messages']}")
        elif response.status_code == 404:
            print("Error: Resource not found")
        else:
            print(f"Error: {e}")
        return None
    
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API server")
        return None
    
    except requests.exceptions.Timeout:
        print("Error: Request timeout")
        return None

# Использование
data = api_request("GET", "api/posts", headers={"Authorization": f"Bearer {TOKEN}"})
if data:
    for post in data.get("posts", []):
        print(f"Post: {post['title']}")
```

---

## JavaScript/Node.js примеры

### Установка

```bash
npm install node-fetch
# или
npm install axios
```

### Пример 1: Использование Fetch API

```javascript
const API_URL = "http://localhost:5000";

// Регистрация пользователя
async function register() {
    const response = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: "js_user",
            password: "securePass123",
            full_name: "JavaScript User"
        })
    });
    
    const data = await response.json();
    console.log("Registration:", data);
    return data;
}

// Вход пользователя
async function login(username, password) {
    const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    console.log("Token:", data.access_token);
    return data.access_token;
}

// Создание поста
async function createPost(token, title, content) {
    const response = await fetch(`${API_URL}/api/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            title,
            content,
            status: "published"
        })
    });
    
    const data = await response.json();
    console.log("Post created:", data);
    return data;
}

// Получение всех постов
async function getAllPosts() {
    const response = await fetch(`${API_URL}/api/posts`);
    const data = await response.json();
    console.log("Posts:", data.posts);
    return data.posts;
}

// Полный пример
async function main() {
    try {
        // Регистрация
        await register();
        
        // Вход
        const token = await login("js_user", "securePass123");
        
        // Создание поста
        await createPost(
            token,
            "JavaScript API Client",
            "This is a blog post created with JavaScript API client"
        );
        
        // Получение постов
        await getAllPosts();
        
    } catch (error) {
        console.error("Error:", error);
    }
}

main();
```

### Пример 2: Использование Axios

```javascript
const axios = require('axios');

const api = axios.create({
    baseURL: 'http://localhost:5000/api'
});

// Добавить интерцептор для автоматического добавления токена
let token = null;

api.interceptors.request.use(config => {
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Вход пользователя
async function login(username, password) {
    try {
        const response = await api.post('/auth/login', {
            username,
            password
        });
        token = response.data.access_token;
        return response.data;
    } catch (error) {
        console.error('Login failed:', error.response.data);
    }
}

// CRUD операции
async function crud() {
    try {
        // Создание
        const createRes = await api.post('/posts', {
            title: 'New Post',
            content: 'Post content with enough characters',
            status: 'published'
        });
        console.log('Created:', createRes.data);
        
        const postId = createRes.data.post.post_id;
        
        // Чтение
        const readRes = await api.get(`/posts/${postId}`);
        console.log('Read:', readRes.data);
        
        // Обновление
        const updateRes = await api.put(`/posts/${postId}`, {
            title: 'Updated Title'
        });
        console.log('Updated:', updateRes.data);
        
        // Удаление
        const deleteRes = await api.delete(`/posts/${postId}`);
        console.log('Deleted:', deleteRes.data);
        
    } catch (error) {
        console.error('Error:', error.response.data);
    }
}

// Использование
async function main() {
    await login('js_user', 'securePass123');
    await crud();
}

main();
```

---

## Postman коллекция

Можно импортировать эту коллекцию в Postman:

```json
{
  "info": {
    "name": "Блог API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/auth/register",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "register"]
            },
            "body": {
              "mode": "raw",
              "raw": "{\"username\": \"testuser\", \"password\": \"pass123\", \"full_name\": \"Test User\"}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": {
              "raw": "{{base_url}}/api/auth/login",
              "host": ["{{base_url}}"],
              "path": ["api", "auth", "login"]
            },
            "body": {
              "mode": "raw",
              "raw": "{\"username\": \"testuser\", \"password\": \"pass123\"}"
            }
          }
        }
      ]
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000"
    },
    {
      "key": "token",
      "value": ""
    }
  ]
}
```

---

## Частые сценарии

### Сценарий 1: Полный блог workflow

```python
import requests
import json

class BlogAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.user = None
    
    def register(self, username, password, full_name):
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={"username": username, "password": password, "full_name": full_name}
        )
        return response.json()
    
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        self.user = data["user"]
        return data
    
    def create_post(self, title, content):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/posts",
            json={"title": title, "content": content},
            headers=headers
        )
        return response.json()
    
    def add_comment(self, post_id, text):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/posts/{post_id}/comments",
            json={"text": text},
            headers=headers
        )
        return response.json()

# Использование
api = BlogAPI()

# 1. Регистрация
api.register("blogger", "password123", "Blog Author")

# 2. Вход
api.login("blogger", "password123")

# 3. Создание поста
post = api.create_post(
    "My First Blog Post",
    "This is my first blog post created with Python API"
)

# 4. Добавление комментария
post_id = post["post"]["post_id"]
api.add_comment(post_id, "Great blog post!")
```

### Сценарий 2: Миграция старого блога

```python
import requests
import csv

api = BlogAPI()

# Вход
api.login("admin", "admin_password")

# Загрузить посты из CSV
with open("old_posts.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        post = api.create_post(row["title"], row["content"])
        print(f"Migrated: {row['title']}")
```

---

**Последнее обновление:** 10 апреля 2024
