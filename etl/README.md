# ETL
## Overview

- Три компонента: Extractor, Transformer, Loader. 
- У Extractor ещё три, каждый отвечает за свой SQL, описанный в теории.
- Всем управляет композиционный класс ETL в `etl.py`. 
- Конфиг через `pydantic_settings`.
- Аннотации типов.
- Поверхностное логирование.
- Сервис elastic в Compose (но без кода).

Работает всё через бесконечный цикл (у той самой морды), который раз в кастомное время проходится по всем записям.

Пачки реализованы только у Producer (первый компонент экстрактора) и у Loader.

### Из того, что не сделано

- State
- Backoff
- Восстановление соединения
- Комментарии к коду
- Создание сервиса по схеме

Многое не успел, на самом деле. Сдаю не потому, что доволен. А из-за жёсткого дедлайна :)

### known features:
Когда записей, сделанных в один TimeStamp > BatchSize, они пропускаются.



## Environment Variables

Все переменные окружения перечислены в .env.template. Только подставить и поменять на `.env`.
## Запуск (RU)

Через `main.py`.

Таймаут по дефолту выставлен 15 сек. Он пройдётся по всем трём таблицам и встанет на sleep.
## Authors

- [Ilya Kabeshov](https://t.me/luchnikkek)

