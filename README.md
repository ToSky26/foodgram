# Foodgram
[Foodgram](https://toskyfoodgram.hopto.org)

## Описание
Foodgram — это веб-сервис для публикации и хранения кулинарных рецептов.

## Функциональность
- регистрация и авторизация пользователей
- добавление и удаление рецептов
- загрузка изображений
- просмотр ленты
---

## Стек технологий
- Python 3.10–3.12
- Django
- PostgreSQL
- Gunicorn
- Nginx
- Docker
- GitHub Actions

---

# Развертывание проекта через Docker

## 1. Клонирование репозитория
```bash
git clone https://github.com/ToSky26/foodgram.git

cd foodgram
```

## 2. Создать файл .env и добавить необходимые переменные окружения
```bash
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
```

## 3. Запуск контейнеров
```bash
docker compose -f docker-compose.production.yml up -d
```

## 4. Выполнение миграций
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

## 5. Сбор статических файлов 
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

## 7. Загрузка данных из фикстур
### Импорт ингредиентов
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py loaddata ingredients.json
```
### Импорт тегов
```bash
docker compose -f docker-compose.production.yml exec backend python manage.py loaddata tags.json
```
## Запуск проекта
После успешного развертывания проект доступен:

Главная страница сервера:
[Foodgram](https://toskyfoodgram.hopto.org)

Документация API:
[API документация](https://toskyfoodgram.hopto.org/api/)

Административная панель:
[Админка](https://toskyfoodgram.hopto.org/admin/)


## Локальное развертывание без Docker

### 1. Клонировать репозиторий

```bash
git clone https://github.com/ToSky26/foodgram.git
cd foodgram
```

### 2. Создать виртуальное окружение
```bash
python3 -m venv venv
```

### Активировать виртуальное окружение.
```bash
source venv/bin/activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Выполнить миграции
```bash
python manage.py migrate
```
## 5. Загрузка тестовых данных
### Импорт ингредиентов
```bash
python manage.py loaddata ingredients.json
```
### Импорт тегов
```bash
python manage.py loaddata tags.json
```

### 6. Запустить сервер разработки
```bash
python manage.py runserver
```
После успешного развертывания проект доступен:

Сервер:
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Админка:
[http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### Переключение между базами данных
Изменить значение переменной USE_SQLITE в файле .env:
USE_SQLITE=True — для SQLit
USE_SQLITE=False — для PostgreSQL


## Автор 
**ФИО:** Сакаева Александра Фархадовна
GitHub: [ToSky26](https://github.com/ToSky26)
