#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def configure_stdout() -> None:
    """Перевести вывод в UTF-8, чтобы печать кириллицы не падала на Windows."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="backslashreplace", line_buffering=True)


def main():
    """Run administrative tasks."""
    configure_stdout()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
