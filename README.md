# 🔐 Система управления доступом (Authorization)

## 📖 Общая концепция

В приложении реализована ролевая модель управления доступом (**RBAC — Role-Based Access Control**).

Доступ к ресурсам определяется на основе:
- аутентификации пользователя (определение личности)
- роли пользователя (определение прав доступа)

---

## 🧩 Структура базы данных

Для реализации системы используются следующие таблицы:

### 1. Users (Пользователи)

| Поле       | Тип     | Описание           |
|------------|---------|--------------------|
| id         | int     | Уникальный ID      |
| first_name | string | Имя пользователя   |
| last_name  | string | Фамилия пользователя |
| email      | string  | Email пользователя   |
| password   | string  | Хэш пароля           |
| role       | enum | Роль пользователя |

---

### 2. Roles (Роли)

- ADMIN  
- USER  
- SUPERUSER

## Доступы

- пользователь может менять и удалять только свои данные
- админ и суперюзер могут менять роли юзеров
- суперюзер создает первого админа

## Создание Superuser

python -m scripts.create_superuser

## Запуск 

```bash
  git clone https://github.com/Kasiet2001/auth_app.git
  cd auth_app
  pip install -r requirements.txt
  alembic upgrade head
```
## Через Docker

``` bash
  docker compose up --build

```