# Foodgram

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

## Установка проекта

### 1. Клонировать репозиторий

```bash
git clone https://github.com/<username>/foodgram.git
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

### 5. Запустить сервер
```bash
python sudo docker compose -f docker-compose.production.yml up -d
```

### Переключение между базами данных
Изменить значение переменной USE_SQLITE в файле .env:
USE_SQLITE=True — для SQLit
USE_SQLITE=False — для PostgreSQL

## Автор 
GitHub: https://github.com/ToSky26
