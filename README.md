# GPT-2 web-service

## Описание проекта

Это интерактивный чат, где вы можете общаться с моделью GPT-2. Просто отправьте сообщение, и модель продолжит ваш текст.

## Структура проекта

```plaintext
project_root/
|
├── app/
|   ├── auth/                   # авторизация, хеширования паролей и парсинг токена
│   ├── consumer-gpu/           # сервис с ml моделью
|   ├── database/               # настройки соединения с базой данных
|   ├── models/                 # ORM модели
|   ├── rabbitmq/               # настройки соединения с rabbitmq
|   ├── routs/                  # FastAPI маршруты
|   ├── services/
|   |   ├── auth/               # способ и форма авторизации
|   |   └── crud/               # сервисы для работы с базой данных и ml моделью
|   ├── test/                   # pytest тесты
|   ├── utils/                  # дополнительные функции (заполнение базы данных)
|   ├── view/                   # Jinj2 html шаблоны
|   ├── .env
|   ├── DockerFile
|   ├── main.py
|   ├── pytest.ini
|   └── requirements.txt
|
├── nginx/
│   └── nginx.conf
|
├── docker-compose.yml
|
├── .env
│
├── .gitignore
|
└── README.md
```

## Инструкция по запуску проекта

- Запустите:
  - `docker-compose build`
  - `docker-compose up`
- дождитесь, пока поднимутся `consumer`-ы;
- иногда `app` с первого раза не может соединиться с `rabbitmq`. Если так, то:
  - `docker-compose stop app`
  - `docker-compose up --no-deps app`

- Прослушиваемые порты:
  - :80 - app;
  - :443 - nginx;
  - :15672 - rabbitmq web интерфейс;
  - :5672 - rabbitmq соединение;
  - :5432 - postgresql

- Аппаратные требования:
  - операционная система: Linux (ubuntu22.04);
  - gpu с поддержкой cuda и объемом видеопамяти >2 гб;

- Инструкции по настройки cuda:
  - [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
