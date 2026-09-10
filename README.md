# Online project — интернет-магазин

Учебный проект SkyPro (блок 6 «Разработка веб-приложений на Django»,
урок 21.2 «Основы вёрстки»).

Две части:

1. **Вёрстка** страниц интернет-магазина на Bootstrap 5.3.3 (CDN).
2. **Веб-сервер** без фреймворков (только стандартная библиотека Python):
   на любой GET-запрос отдаёт страницу «Контакты», принимает POST
   и печатает данные формы в консоль, обрабатывает ошибки 404 и 500.

## Требования

- Python 3.13
- [Poetry](https://python-poetry.org/) для управления зависимостями
- Выход в интернет для загрузки Bootstrap с CDN

## Установка

```bash
poetry install
```

Рантайм-зависимостей у проекта нет — `poetry install` ставит только
инструменты разработки (`black`, `isort`, `flake8`, `mypy`).

## Запуск сервера

```bash
poetry run python server.py
```

После старта в консоли появится:

```
Сервер запущен: http://localhost:8000
```

Хост и порт заданы константами `HOST` и `PORT` в `server.py`.
Остановка — `Ctrl+C`.

### Поведение

| Запрос | Ответ |
|---|---|
| `GET` на любой путь | `templates/contacts.html`, `200`, `Content-Type: text/html; charset=utf-8` |
| `POST` на любой путь | данные формы печатаются в консоль, в ответ — та же страница «Контакты», `200` |
| шаблон не найден на диске | `templates/404.html`, статус `404` |
| другая внутренняя ошибка | `templates/500.html`, статус `500` |

Шаблон читается из файла через контекстный менеджер `with open(...)`
на каждый запрос.

### Примеры запросов

```bash
# GET
curl -i http://localhost:8000/

# POST с данными формы (тело в UTF-8)
curl -i -X POST http://localhost:8000/ \
  --data "name=%D0%98%D0%B2%D0%B0%D0%BD&email=ivan%40mail.ru&message=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82"
```

В консоли сервера появится:

```
Получен POST-запрос, данные формы:
  name = Иван
  email = ivan@mail.ru
  message = Привет
```

Или просто открыть <http://localhost:8000/> в браузере и отправить
форму со страницы «Контакты».

## Страницы (`templates/`)

| Файл | Назначение |
|---|---|
| `main.html` | Главная — эталонная обвязка (хедер, меню, футер) |
| `catalog.html` | Каталог — 4 карточки-заглушки по 2 в ряд |
| `category.html` | Категория 1 — 6 карточек товара по 3 в ряд |
| `contacts.html` | Контакты — форма обратной связи + блок контактов |
| `404.html` | Страница ошибки «не найдено» |
| `500.html` | Страница внутренней ошибки сервера |

Обвязка на всех страницах одинаковая, взята из `main.html`.
Bootstrap подключается только с CDN, локальных копий нет.

## Структура проекта

```
Online_project_full/
├── templates/            # HTML-страницы
│   ├── main.html
│   ├── catalog.html
│   ├── category.html
│   ├── contacts.html
│   ├── 404.html
│   └── 500.html
├── server.py             # веб-сервер на http.server
├── Claude_code/          # ТЗ, прототипы, отчёт о работе
│   ├── TZ.md
│   └── report.md
├── pyproject.toml        # зависимости, настройки black/isort/mypy
├── .flake8               # настройки flake8
├── poetry.lock
└── README.md
```

## Проверка качества кода

```bash
poetry run isort .
poetry run black .
poetry run flake8 .
poetry run mypy .
```

Порядок важен: сначала форматтеры (`isort`, `black`), затем линтеры
(`flake8`, `mypy`). Настройки — в `pyproject.toml` и `.flake8`
(`max-line-length = 119`).
