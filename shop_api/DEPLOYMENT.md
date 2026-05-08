# Руководство по развёртыванию Блог API на PythonAnywhere

## Предварительные требования

- Аккаунт на [PythonAnywhere](https://www.pythonanywhere.com)
- Репозиторий на GitHub или другом сервисе Git
- Исходный код проекта

## Пошаговое развёртывание

### Шаг 1: Создание аккаунта на PythonAnywhere

1. Перейти на https://www.pythonanywhere.com
2. Нажать "Sign up now" или "Start exploring"
3. Создать бесплатный аккаунт
4. Подтвердить email

### Шаг 2: Загрузка кода проекта

#### Способ A: Из GitHub (рекомендуется)

```bash
# В консоли PythonAnywhere
cd ~
git clone https://github.com/your-username/blog_api.git
cd blog_api
```

#### Способ B: Через веб-интерфейс

1. В PythonAnywhere → Files
2. Загрузить файлы вручную
3. Или использовать форму загрузки

### Шаг 3: Установка виртуального окружения

```bash
cd ~/blog_api
mkvirtualenv --python=/usr/bin/python3.8 blog_env
workon blog_env
pip install -r requirements.txt
```

### Шаг 4: Инициализация базы данных

```bash
workon blog_env
cd ~/blog_api
python run.py db upgrade
python run.py seed-db
```

### Шаг 5: Настройка WSGI приложения

1. В PythonAnywhere панели: **Web** → **Add new web app**
2. Выбрать **Manual configuration**
3. Выбрать **Python 3.8**
4. Редактировать WSGI configuration file:

```python
# /var/www/username_pythonanywhere_com_wsgi.py

import sys
import os

# Добавить путь к проекту
project_folder = os.path.expanduser('~/blog_api')
sys.path.insert(0, project_folder)

# Установить переменные окружения
os.chdir(project_folder)

# Импортировать приложение Flask
from run import app as application
```

### Шаг 6: Настройка статических файлов (если нужны)

1. В PythonAnywhere: **Web** → **Static files**
2. Нажать **Add a new static files entry**
   - URL: `/static/`
   - Directory: `/home/username/blog_api/static`

### Шаг 7: Настройка переменных окружения

Создать файл `.env.pythonanywhere` в корне проекта:

```
FLASK_ENV=production
DATABASE_URL=sqlite:////home/username/blog_api/instance/blog.db
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
```

Хотя PythonAnywhere использует файловую систему, для продакшена рекомендуется использовать PostgreSQL.

### Шаг 8: Настройка базы данных PostgreSQL (рекомендуется для продакшена)

1. Основной аккаунт на PythonAnywhere включает доступ к PostgreSQL
2. Создать новую БД:
   ```bash
   # В консоли PythonAnywhere
   python
   >>> import psycopg2
   >>> # Подключиться и создать БД
   ```

3. Обновить `DATABASE_URL` в конфигурации

### Шаг 9: Перезагрузка приложения

1. В PythonAnywhere: **Web**
2. Нажать зелёную кнопку **Reload**
3. Проверить логи ошибок если что-то пошло не так

### Шаг 10: Проверка работы

```bash
curl https://username.pythonanywhere.com/
# Должна вернуться ошибка 404 или ответ API
```

## Управление приложением

### Просмотр логов

В PythonAnywhere:
- **Error log**: Ошибки приложения
- **Server log**: Логи сервера
- **Access log**: Логи запросов

Или в консоли:
```bash
tail -f ~/blog_api/logs/blog_api.log
```

### Обновление кода

```bash
cd ~/blog_api
git pull origin main
workon blog_env
pip install -r requirements.txt
# Перезагрузить в веб-интерфейсе PythonAnywhere
```

### Резервное копирование базы данных

```bash
# Создать бэкап SQLite
cp ~/blog_api/instance/blog.db ~/blog_api/instance/blog.db.backup

# Или выгрузить PostgreSQL
pg_dump -h localhost -U username blog_db > ~/backups/blog_db.sql
```

## Оптимизация для Production

### 1. Настройка SSL/HTTPS

- На бесплатном плане: автоматически
- Перейти на HTTPS в конфигурации

### 2. Увеличение лимитов PythonAnywhere

- Обновить аккаунт для большего количества запросов
- Оплатить Premium план

### 3. Кэширование

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/posts')
@cache.cached(timeout=300)
def get_posts():
    # ...
```

### 4. Сжатие ответов

```python
from flask_compress import Compress

Compress(app)
```

### 5. Настройка Gunicorn

Если переходить на выделенный сервер, использовать:

```bash
gunicorn --workers 4 --threads 2 --worker-class gthread \
         --bind 0.0.0.0:5000 --timeout 60 run:app
```

## Решение проблем

### Ошибка: "ModuleNotFoundError: No module named 'app'"

Решение:
```bash
workon blog_env
pip install -r requirements.txt
```

### Ошибка: "database is locked"

Решение:
```bash
# Перемигрировать БД
python run.py db downgrade base
python run.py db upgrade
```

### Ошибка: "Permission denied" для логов

Решение:
```bash
mkdir -p ~/blog_api/logs
chmod 755 ~/blog_api/logs
```

### Приложение запускается медленно

- Проверить логи: **Error log** в PythonAnywhere
- Увеличить вычислительные ресурсы
- Оптимизировать запросы БД

## Мониторинг

### Настройка алертов

1. В PythonAnywhere: **Account**
2. Настроить email оповещений

### Метрики производительности

```bash
# Просмотреть статистику в логе
tail -f ~/blog_api/logs/blog_api.log | grep "ERROR"
```

## Масштабирование

Для большой нагрузки:

1. Перейти на выделенный сервер
2. Использовать PostgreSQL вместо SQLite
3. Добавить Redis для кэша и очередей
4. Настроить Load Balancing
5. Использовать Content Delivery Network (CDN)

## Резервные копии и восстановление

### Автоматические бэкапы

Создать cron job:

```bash
crontab -e

# Добавить строку:
0 2 * * * /home/username/backup_script.sh
```

Содержимое `backup_script.sh`:

```bash
#!/bin/bash
DB_PATH="/home/username/blog_api/instance/blog.db"
BACKUP_DIR="/home/username/backups"
DATE=$(date +\%Y\%m\%d_\%H\%M\%S)

mkdir -p $BACKUP_DIR
cp $DB_PATH $BACKUP_DIR/blog_db_$DATE.db

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "blog_db_*.db" -mtime +30 -delete
```

## Важные заметки безопасности

⚠️ **Никогда**:
- Не коммитить `.env` файл в Git
- Не использовать дефолтные JWT_SECRET_KEY на продакшене
- Не отключать HTTPS
- Не хранить чувствительные данные в коде

✅ **Всегда**:
- Используйте переменные окружения для конфиденциальных данных
- Регулярно обновляйте зависимости
- Проверяйте логи на ошибки
- Делайте резервные копии БД
- Используйте HTTPS только

## Контакт с поддержкой PythonAnywhere

- Website: https://www.pythonanywhere.com
- Help forums: https://www.pythonanywhere.com/forums/
- Email support: support@pythonanywhere.com

---

**Последнее обновление:** 10 апреля 2024  
**Автор:** Блог API Team
