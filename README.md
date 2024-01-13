# Sprint 2

A project for second sprint for Yandex Middle Python Course.


## Environment Variables

To run this project, you will need to:
- Change the environment variables from `.env.template` and rename it to `.env`.
- Change the environment variables to db service in the `docker-compose.yml`.


## Deployment (RU)

Для деплоя нужен именованный volume db-volume с Postgres базой данных _(я не совсем понимаю, как это ещё может быть реализовано, но готов переделать)_.

#### Создать суперпользователя
Создаём с log:pass=admin:123123

```bash
  make admin
```

#### Запуск
_docker compose up в detached-режиме и с пересборкой_

```bash
  make start
```

#### Остановка
_docker compose down_

```bash
  make stop
```
## API Reference

#### Get all items

```http
  GET /api/v1/movies
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `page`    | `string` | Page number *(default=1)* |

#### Get item by uuid

```http
  GET /api/v1/movies/${uuid}
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `uuid`    | `string` | **Required**. UUID of movie to fetch |


## Authors

- [Ilya Kabeshov](https://t.me/luchnikkek)