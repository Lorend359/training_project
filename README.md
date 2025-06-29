## Приложение `users`

Реализует систему регистрации и JWT-аутентификации.

### Регистрация
- `POST /api/users/register/`
- Поля: `email`, `full_name`, `password`
- Создаёт нового пользователя.

### JWT-аутентификация
- `POST /api/users/token/` — вход, возвращает `access` и `refresh`
- `POST /api/users/token/refresh/` — обновление access-токена

### Прочее
- Используется кастомная модель пользователя (`CustomUser`)
- Авторизация по email
- Подключена библиотека `djangorestframework-simplejwt`
