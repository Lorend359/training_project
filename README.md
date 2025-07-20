# LMS — Платформа самообучения для пенсионеров

> **Дипломный проект** по курсу Python / Django.
> Платформа помогает преподавателям создавать адаптированные курсы по смартфонам для пенсионеров, а студентам — учиться и проходить тесты в простом, дружелюбном формате.

---

## ✨ Что реализовано

| Блок                 | Кратко                                     | Подробности                                                                                         |
| -------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------- |
| **Авторизация**      | JWT (Access/Refresh)                       | `users/urls.py` — вход, регистрация. Кастомная модель `CustomUser` (email → username).              |
| **Роли**             | Админ • Преподаватель • Студент            | Команда `python manage.py init_groups` — группы и granular-permissions.                             |
| **Курсы и уроки**    | CRUD через admin + REST                    | `CourseViewSet`, `LessonViewSet`: преподаватель управляет только своими объектами, видит все курсы. |
| **Тесты знаний**     | Тест (Assessment) на урок, вопросы, ответы | Проверка через отдельный эндпоинт `POST /api/v1/submit-answer/`. 3 попытки, одна правильная запись. |
| **Документация API** | Swagger / OpenAPI 3                        | `/api/docs/`, генерируется через drf-spectacular.                                                   |
| **Безопасность**     | CORS, CSRF, JWT                            | `settings.py` → CORS\_ALLOWED\_ORIGINS.                                                             |
| **Тесты**            | 608 строк, покрытие **83 %**               | `pytest`, `coverage`. HTML-отчёт — `htmlcov/index.html`.                                            |
| **Код-стиль**        | flake8, black, isort, mypy                 | Конфиги в pyproject.toml и .flake8.                                                                 |
| **CI-ready**         | Линтеры и тесты                            | Достаточно 20 строк GitHub Actions для автопрогона.                                                 |

---

## 🏗️ Технический стек

* Python 3.12, Django 5.2, Django REST Framework 3.16
* PostgreSQL (или любой совместимый сервер — настраивается через .env)
* JWT — djangorestframework-simplejwt
* drf-spectacular — автогенерация OpenAPI 3 + Swagger UI
* django-filters — ordering и фильтрация
* Poetry — управление зависимостями
* flake8, black, isort, mypy — линтеры

---

## 🚀 Быстрый старт

```bash
# Клонируем репозиторий
$ git clone https://github.com/<your-username>/training_project.git
$ cd training_project

# Устанавливаем зависимости
$ poetry install

# Конфиг переменных (пример ниже)
$ cp .env .env.local && nano .env.local

# Миграции + группы/права
$ poetry run python manage.py migrate
$ poetry run python manage.py init_groups

# Запуск сервера
$ poetry run python manage.py runserver 0.0.0.0:8000

# Открыть документацию
http://localhost:8000/api/docs/
```

### .env (пример)

```env
SECRET_KEY=super-secret-key
DEBUG=True
POSTGRES_DB=training_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_pass
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
ALLOWED_HOSTS=127.0.0.1,localhost
```

> **tip 🖥️** После тестов создаётся HTML-отчёт покрытия (папка `htmlcov`). Откройте `htmlcov/index.html` в браузере — удобно для ручной проверки кода преподавателем.

---

## 🧪 Тесты и покрытие

```bash
# Линтеры
poetry run flake8

# Юнит- и API-тесты
poetry run pytest -q

# Покрытие кода
poetry run coverage run -m pytest
poetry run coverage html  # отчёт в htmlcov/
```

* **Всего строк:** 608
* **Покрыто:** 83 %
* **Файлы 100% покрытия:** admin, migrations, команды, tests

---

## 📂 Структура проекта

```
training_project/
├─ assessments/   # тесты, вопросы, ответы, сервис-слой
├─ courses/       # курсы, уроки, permissions
├─ users/         # кастом-юзер, регистрация, JWT
├─ core/constants.py   # названия групп
├─ config/        # настройки Django + URL-маршруты
├─ manage.py
└─ README.md
```

---

## 🔒 Права доступа (RBAC)

| Роль              | Просмотр                  | Создание \ Изменение \ Удаление     |
| ----------------- | ------------------------- | ----------------------------------- |
| **Администратор** | ✅ все сущности            | ✅ все сущности                      |
| **Преподаватель** | ✅ все курсы, уроки, тесты | ✅ **только свои** курсы/уроки/тесты |
| **Студент**       | ✅ все курсы, уроки, тесты | ❌ (кроме отправки ответов)          |

Permission-классы:

* `IsAdminOrTeacher` — роль-based доступ
* `IsOwnerOrAdmin` — object-level доступ в `courses`
* `IsCourseOwnerOrPrivileged` — object-level доступ в `assessments`

---

## 🧑‍💻 Примеры API-запросов

### Регистрация пользователя

```http
POST /api/users/register/
Content-Type: application/json
{
  "email": "test@example.com",
  "full_name": "Пётр Петров",
  "password": "12345pass"
}
```

### Отправка ответа на тест

```http
POST /api/v1/submit-answer/
Content-Type: application/json
{
  "question": 1,
  "selected_option": 2
}
```

Ответ:

```json
{
  "is_correct": true,
  "attempt_number": 1,
  "detail": "Ответ принят"
}
```

---

## 🛣️ Дорожная карта (что можно сделать дальше)

1. **Telegram-бот (интерактивный LMS):**

   > Задумка — чтобы пенсионеры могли проходить уроки и тесты прямо в Telegram: получать напоминания, отвечать на вопросы, видеть свой прогресс без браузера. Вся логика LMS дублируется внутри бота — структура курсов, попытки, лимиты и обратная связь доступны в диалоге с ботом.

2. **Справочник / база знаний:**

   > FAQ по смартфонам, агрегированные инструкции и советы, структурированные для быстрого поиска и самостоятельного освоения.

3. **Docker-compose для деплоя** (PostgreSQL + app)

4. **CI/CD:** GitHub Actions → Fly.io / любой хостинг с Docker

---

## 🔗 Полезные ссылки

* **Swagger UI:** `http://<host>:8000/api/docs/` (OpenAPI 3)
* **HTML-coverage:** `htmlcov/index.html`
* **Django admin:** `http://<host>:8000/admin/` (создать суперпользователя: `python manage.py createsuperuser`)

---

© 2025 — Святослав. Проект создан в учебных целях, свободно расширяем под нужды преподавателей и пенсионеров.
По вопросам сотрудничества: [arend359@gmail.com](mailto:arend359@gmail.com)
