📌 Описание проекта
REST API-сервис для приёма, хранения и модерации информации о перевалах.
Проект выполнен в рамках обучения. API реализован на Flask + PostgreSQL.

Функциональность:

Добавление нового перевала (POST)

Получение перевала по id (GET)

Обновление перевала (PATCH, если статус new)

Получение всех перевалов по email пользователя (GET)

⚙️ Установка и запуск

# Установка зависимостей
pip install -r requirements.txt

# Установка переменных окружения
export FSTR_DB_HOST=localhost
export FSTR_DB_PORT=5432
export FSTR_DB_LOGIN=postgres
export FSTR_DB_PASS=yourpassword

# Запуск Flask-сервера
python app.py

🔌 Описание методов API

✅ POST /submitData
Добавляет информацию о перевале.

Пример запроса:

POST /submitData
Content-Type: application/json

{
  "beauty_title": "пер.",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "user": {
    "email": "user@email.tld",
    "phone": "79031234567",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович"
  },
  "coords": {
    "latitude": "45.3842",
    "longitude": "7.1525",
    "height": "1200"
  },
  "level": {
    "winter": "",
    "summer": "1А",
    "autumn": "1А",
    "spring": ""
  },
  "images": [
    {"id": 1, "title": "Седловина"},
    {"id": 2, "title": "Подъем"}
  ]
}
Ответ:
{
  "status": 200,
  "message": null,
  "id": 42
}

🔍 GET /submitData/<id>
Получает информацию о перевале по ID.

Пример:

GET /submitData/42

Ответ:
{
  "status": 200,
  "data": {
    "id": 42,
    "raw_data": { ... },
    "images": [ ... ],
    "status": "new",
    "moderated_at": null
  }
}

✏️ PATCH /submitData/<id>
Обновляет данные о перевале, если статус — new. Нельзя менять поля пользователя.

Пример:

PATCH /submitData/42
Content-Type: application/json

{
  "beauty_title": "пер. обновленный",
  "title": "Новый перевал",
  "coords": { ... },
  "level": { ... },
  "images": [ ... ],
  "user": {
    "email": "user@email.tld",
    "phone": "79031234567",
    "fam": "Пупкин",
    "name": "Василий",
    "otc": "Иванович"
  }
}

Ответ:
{
  "state": 1,
  "message": "Record updated successfully"
}

📧 GET /submitData/?user__email=<email>
Выдаёт список перевалов, отправленных указанным пользователем.

GET /submitData/?user__email=user@email.tld

Ответ:
{
  "status": 200,
  "data": [
    {
      "id": 42,
      "status": "new",
      "raw_data": { ... }
    },
    ...
  ]
}
