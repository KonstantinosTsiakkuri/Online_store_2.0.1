"""Контроллеры приложения catalog."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Главная страница с карточками товаров."""
    return render(request, "catalog/home.html")


def contacts(request: HttpRequest) -> HttpResponse:
    """Страница контактов: при POST печатает данные формы в консоль."""
    if request.method == "POST":
        name = request.POST.get("name", "")
        phone = request.POST.get("phone", "")
        message = request.POST.get("message", "")
        print("Получено сообщение с формы обратной связи:")
        print(f"  Имя: {name}")
        print(f"  Телефон: {phone}")
        print(f"  Сообщение: {message}")
    return render(request, "catalog/contacts.html")
