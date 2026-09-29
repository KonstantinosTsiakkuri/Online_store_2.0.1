# Online project — интернет-магазин на Django

Учебный проект SkyPro (блок 6 «Разработка веб-приложений на Django»).
Сайт интернет-магазина: главная страница с карточками товаров и страница
контактов с формой обратной связи.

Проект развивается от урока к уроку:

- **урок 21.2** — вёрстка страниц на Bootstrap и простой веб-сервер
  на `http.server` без фреймворков (`server.py`, папка `templates/`);
- **урок 22** — перевод проекта на Django: проект `config`, приложение
  `catalog`, маршрутизация, шаблоны и контроллеры.

## Стек

- Python 3.13
- Django 5.2
- Bootstrap 5.3.3 (подключается с CDN)
- SQLite (база по умолчанию)
- Poetry — управление зависимостями
- black, isort, flake8, mypy — форматирование и проверка кода

## Требования

- Python 3.13 или новее
- [Poetry](https://python-poetry.org/) (либо `pip` + `venv`)
- Выход в интернет — Bootstrap загружается с CDN

## Установка

### 1. Клонировать репозиторий

```bash
git clone <адрес-репозитория>
cd Online_project_full
```

### 2. Создать окружение и установить зависимости

**Вариант А — Poetry (рекомендуется):**

```bash
poetry install
```

Все команды ниже запускаются через `poetry run ...` либо внутри
`poetry shell`.

**Вариант Б — venv + pip:**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
pip install -r requirements.txt
```

## Запуск

```bash
python manage.py migrate      # применить миграции (создаст db.sqlite3)
python manage.py runserver    # запустить сервер разработки
```

Сайт будет доступен по адресу <http://127.0.0.1:8000/>.
Остановка сервера — `Ctrl+C`.

Дополнительно можно создать администратора для доступа в админку:

```bash
python manage.py createsuperuser
```

## Страницы

| Адрес | Название | Что на странице |
|---|---|---|
| `/` | Главная | Заголовок, описание магазина, три карточки товаров |
| `/contacts/` | Контакты | Контактные данные и форма обратной связи (имя, телефон, сообщение) |
| `/admin/` | Админка | Стандартная админ-панель Django |

Данные, отправленные через форму на странице контактов, выводятся
в консоль запущенного сервера.

## Структура проекта

```
Online_project_full/
├── manage.py                  # точка входа Django
├── config/                    # пакет настроек проекта
│   ├── settings.py            # настройки (приложения, шаблоны, БД, локаль)
│   ├── urls.py                # корневая маршрутизация, подключает catalog
│   ├── wsgi.py
│   └── asgi.py
├── catalog/                   # основное приложение
│   ├── urls.py                # маршруты приложения (app_name = "catalog")
│   ├── views.py               # контроллеры home и contacts
│   ├── templates/catalog/
│   │   ├── home.html          # шаблон главной страницы
│   │   └── contacts.html      # шаблон страницы контактов
│   ├── models.py
│   ├── admin.py
│   ├── apps.py
│   ├── tests.py
│   └── migrations/
├── templates/                 # вёрстка из урока 21.2 (статические HTML)
├── server.py                  # сервер из урока 21.2 (http.server, без Django)
├── Claude_code/               # ТЗ, прототипы и отчёты по домашним работам
├── requirements.txt           # зависимости для pip
├── pyproject.toml             # зависимости и настройки black/isort/mypy
├── poetry.lock
├── .flake8                    # настройки flake8
├── .gitignore
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
(`flake8`, `mypy`). Длина строки — 119 символов, миграции из проверок
исключены.
