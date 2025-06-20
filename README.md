# Система email-уведомлений

Сервис для управления и отправки email-рассылок при помощи SMTP с авторизацией и очередями задач. Позволяет создавать кампании, планировать отправку уведомлений получателям и обрабатывать статусы сообщений с использованием FastAPI, RabbitMQ и Docker.

## Содержание

* [Технологии](#технологии)
* [Начало работы](#начало-работы)
* [Примеры использования API](#примеры-использования-api)
* [Тестирование](#тестирование)
* [Deploy и CI/CD](#deploy-и-cicd)
* [Команда проекта](#команда-проекта)

## Технологии

* [Python](https://www.python.org/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [SQLAlchemy](https://www.sqlalchemy.org/)
* [Alembic](https://alembic.sqlalchemy.org/)
* [RabbitMQ](https://www.rabbitmq.com/)
* [Pydantic-settings](https://docs.pydantic.dev/latest/api/pydantic_settings/)
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* [pytest](https://docs.pytest.org/en/stable/)
* [JWT](https://jwt.io/)
* [mypy](https://mypy-lang.org/)
* [flake8](https://flake8.pycqa.org/en/latest/)

## Начало работы

### Требования

* Python 3.12+
* Docker и Docker Compose
* RabbitMQ (в контейнере или внешне)
* PostgreSQL (в контейнере или внешне)

### Установка и запуск

1. Клонируйте репозиторий:

```sh
git clone https://github.com/AlexeyPetrochenko/Notification_service_FastAPI.git
cd Notification_service_FastAPI
```
2. Создайте почту с которой будет происходить отправка уведомлений и получите пароль приложения от SMTP-сервиса:
- Войдите в почту mail.ru через веб-интерфейс.
Перейдите на https://mail.ru и авторизуйтесь.
- Откройте настройки аккаунта.
Нажмите на аватар в правом верхнем углу → выберите «Настройки» → «Безопасность».
- Создайте пароль приложения.
В разделе «Пароли приложений» или «Пароли для сторонних приложений» нажмите «Создать новый пароль».
Введите название (например, «Backend Email Sender») и сохраните сгенерированный пароль.
- Используйте этот пароль в конфигурации SMTP.
В .env или настройках проекта укажите:

3. Получите токен доступа для воркеров
- запустите только api и БД
```sh
docker compose up app db
```
- пошлите запрос на апи для регистрации и логина для получения токена
```sh
curl -X POST "http://localhost:8000/users/register/" -H "Content-Type: application/json" -d '{"email":"worker@example.com", "password":"yourpassword"}'
curl -X POST "http://localhost:8000/users/login/" -d "username=worker@example.com&password=yourpassword"
```
- скопируйте токен из ответа он понадобится в .env файле
4. Скопируйте `.env-example` в `.env` и настройте переменные окружения.

5. Запустите контейнеры с помощью Docker Compose:

```sh
docker compose up --build
```

6. Open API будет доступен по адресу [http://localhost:8000/docs](http://127.0.0.1:8000/docs#/)

## Примеры использования API
После запуска сервиса вы можете:
- Зарегистрироваться `POST /users/register`
- Залогиниться и получить JWT токен `POST /users/login`
- Добавить получателей через `POST /recipients/`
- Создать кампанию через `POST /campaigns/`

После добавления кампании, она автоматически запустится воркером в назначенное время.

Ознакомьтесь с документацией по адресу [http://localhost:8000/docs](http://localhost:8000/docs)

## Тестирование

Для запуска тестов используется pytest с моками и httpx (для создания асинхронного клиента приложения). А также требуется запуск тестовой базы данных для интеграционных тестов.
```sh
docker compose up test_db -d
```
```sh
python3 -m pytest .
```

Отчёт о покрытии тестами будет выведен в консоль.

## Deploy и CI/CD

* CI настроен через GitHub Actions для проверки кода, линтинга и тестов.
* Docker-образы собираются и публикуются в DockerHub.
* Автоматический деплой реализован через соответствующие пайплайны. publish.yml


## Команда проекта

* Алексей Петроченко — Backend-разработчик, автор и поддержка проекта
  Контакты: [GitHub](https://github.com/AlexeyPetrochenko) | [Telegram](https://t.me/AlekseyPetrochenko) | [alexeypetrochenko1@gmail.com](mailto:alexeypetrochenko1@gmail.com)

## Источники

* Курс Advanced Learn Python от MoscowPython
* Документация FastAPI, SQLAlchemy, RabbitMQ, Docker
* Вдохновлялся примерами микросервисных архитектур на Python
