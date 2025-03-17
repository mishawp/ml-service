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
├── init-database.sh            # скрипт инициализации базы данных в docker-compose
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

- Тестирование:
  - чтобы запустить тесты измените `engine = create_engine(get_db_settings().DATABASE_URL_psycopg)` на `engine = create_engine(get_db_settings().DATABASE_URL_test.replace("localhost", "database")` в файле `./app/consumer/model.py`;
  - запустите
    - `docker-compose build database rabbitmq consumer`
    - `docker-compose up database rabbitmq consumer`
  - перейдите в директорию `/app` (`cd ./app`);
  - запустите `pytest`;
  - важно: директория `postgres_data` при первой сборке и запуске `docker-compose up` не должен существовать. Иначе скрипт `init-database.sh` не запуститься;
  - не забудьте заменить обратно `engine = create_engine(get_db_settings().DATABASE_URL_psycopg)` на `engine = create_engine(get_db_settings().DATABASE_URL_test.replace("localhost", "database")`  на `engine = create_engine(get_db_settings().DATABASE_URL_psycopg)` в файле `./app/consumer/model.py`;
  - также порты в docker и на хосте должны совпадать.

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
