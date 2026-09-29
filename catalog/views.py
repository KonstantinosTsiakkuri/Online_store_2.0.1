"""Контроллеры приложения catalog."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import FeedbackForm
from catalog.models import Product


def home(request: HttpRequest) -> HttpResponse:
    """Главная страница со списком товаров из базы."""
    products = Product.objects.all()
    return render(request, "catalog/home.html", {"products": products})


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Детальная страница товара. Несуществующий pk даёт 404."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})


def contacts(request: HttpRequest) -> HttpResponse:
    """Страница контактов с формой обратной связи."""
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()
            print("Получено сообщение с формы обратной связи:")
            print(f"  Имя: {feedback.name}")
            print(f"  Телефон: {feedback.phone}")
            print(f"  Сообщение: {feedback.message}")
            messages.success(request, "Спасибо! Ваше сообщение отправлено.")
            return redirect("catalog:contacts")
    else:
        form = FeedbackForm()
    return render(request, "catalog/contacts.html", {"form": form})
