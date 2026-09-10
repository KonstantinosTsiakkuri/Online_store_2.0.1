"""Простое веб-приложение на стандартной библиотеке Python.

На любой GET-запрос сервер возвращает страницу «Контакты». POST-запрос
принимается, а все переданные поля формы печатаются в консоль. Если шаблон
не найден на диске — отдаётся страница 404, при любой другой внутренней
ошибке — страница 500.
"""

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

HOST = "localhost"
PORT = 8000

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

CONTACTS_TEMPLATE = "contacts.html"
NOT_FOUND_TEMPLATE = "404.html"
SERVER_ERROR_TEMPLATE = "500.html"


def configure_stdout() -> None:
    """Перевести консольный вывод в UTF-8, чтобы кириллица не ломала печать."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace", line_buffering=True)


def read_template(name: str) -> str:
    """Прочитать HTML-шаблон из папки templates через контекстный менеджер."""
    path = TEMPLATES_DIR / name
    with open(path, encoding="utf-8") as file:
        return file.read()


class ShopHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов интернет-магазина."""

    def _send_html(self, status: int, html: str) -> None:
        """Отправить клиенту HTML-ответ с указанным статусом."""
        payload = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _serve_contacts(self) -> None:
        """Отдать страницу «Контакты», подменив ответ на 404/500 при ошибке."""
        try:
            self._send_html(200, read_template(CONTACTS_TEMPLATE))
        except FileNotFoundError:
            self._send_fallback(404, NOT_FOUND_TEMPLATE, "404 Not Found")
        except Exception:  # noqa: BLE001 - любая иная ошибка -> страница 500
            self._send_fallback(500, SERVER_ERROR_TEMPLATE, "500 Internal Server Error")

    def _send_fallback(self, status: int, template_name: str, plain_text: str) -> None:
        """Отдать страницу ошибки; если и её нет — короткий текстовый ответ."""
        try:
            self._send_html(status, read_template(template_name))
        except OSError:
            self._send_html(status, f"<h1>{plain_text}</h1>")

    def do_GET(self) -> None:  # noqa: N802 - имя задано BaseHTTPRequestHandler
        """На любой путь вернуть страницу «Контакты»."""
        self._serve_contacts()

    def do_POST(self) -> None:  # noqa: N802 - имя задано BaseHTTPRequestHandler
        """Принять данные формы, напечатать их в консоль и вернуть «Контакты»."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        raw_body = self.rfile.read(length).decode("utf-8", errors="replace")
        form = parse_qs(raw_body, keep_blank_values=True)

        print("Получен POST-запрос, данные формы:")
        if form:
            for field, values in form.items():
                for value in values:
                    print(f"  {field} = {value}")
        else:
            print("  (данные отсутствуют)")

        self._serve_contacts()


def main() -> None:
    """Запустить сервер и слушать запросы до Ctrl+C."""
    configure_stdout()
    server = HTTPServer((HOST, PORT), ShopHandler)
    print(f"Сервер запущен: http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
