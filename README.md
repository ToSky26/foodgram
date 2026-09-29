# 🍽 Foodgram

Веб-сервис для публикации и хранения кулинарных рецептов.

Пользователи могут создавать и удалять рецепты, загружать изображения и просматривать ленту публикаций.

## 🚀 Возможности

* регистрация и авторизация пользователей;
* создание и удаление рецептов;
* загрузка изображений;
* просмотр ленты рецептов;
* работа с ингредиентами и тегами;
* административная панель;
* REST API.

## 🛠 Технологии

* **Python**
* **Django**
* **Django REST Framework**
* **PostgreSQL**
* **Gunicorn**
* **Nginx**
* **Docker**
* **GitHub Actions**

## 💻 Что реализовано

* разработана backend-часть приложения на Django;
* реализована регистрация и авторизация пользователей;
* реализована работа с рецептами и изображениями;
* настроена работа с PostgreSQL;
* реализован REST API;
* настроена контейнеризация приложения с помощью Docker;
* настроены Nginx и Gunicorn;
* настроен CI/CD с использованием GitHub Actions.

## Запуск проекта через Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/ToSky26/foodgram.git
cd foodgram
```

### 2. Создание файла `.env`

Создайте файл `.env` и добавьте необходимые переменные окружения:

```env
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432
```

> Не добавляйте файл `.env` в Git. Он содержит конфиденциальные данные.

### 3. Запуск контейнеров

```bash
docker compose -f docker-compose.production.yml up -d
```

### 4. Выполнение миграций

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

### 5. Сбор статических файлов

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --no-input
```

### 6. Загрузка данных из фикстур

Загрузка ингредиентов:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py loaddata ingredients.json
```

Загрузка тегов:

```bash
docker compose -f docker-compose.production.yml exec backend python manage.py loaddata tags.json
```

## 🖥 Локальный запуск без Docker

### 1. Клонирование репозитория

```bash
git clone https://github.com/ToSky26/foodgram.git
cd foodgram
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
```

Активация:

**Linux/macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Выполнение миграций

```bash
python manage.py migrate
```

### 5. Загрузка тестовых данных

```bash
python manage.py loaddata ingredients.json
python manage.py loaddata tags.json
```

### 6. Запуск сервера разработки

```bash
python manage.py runserver
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000/
```

## 🗄 Работа с базами данных

Для переключения между SQLite и PostgreSQL используется переменная окружения:

```env
USE_SQLITE=True
```

для SQLite и:

```env
USE_SQLITE=False
```

для PostgreSQL.

📌 Статус проекта<br>
Учебный проект в рамках обучения backend-разработке на Python.<br>
Проект разворачивался на удалённом сервере с использованием Docker, Nginx, Gunicorn и PostgreSQL.

👩‍💻 Автор<br>
Сакаева Александра<br>
**GitHub:** [ToSky26](https://github.com/ToSky26)

