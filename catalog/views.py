"""Контроллеры приложения catalog."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from catalog.forms import FeedbackForm, ProductForm
from catalog.models import Product


class ProductListView(ListView):
    """Главная страница: список всех товаров из базы. Доступна анонимам."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Детальная страница товара. Доступна только авторизованным, иначе редирект на вход."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создание нового товара. Доступно только авторизованным."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        """
        После создания переходим на карточку нового товара.

        Статический success_url тут не подходит: адрес зависит от pk,
        который появляется только после сохранения объекта.
        """
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование существующего товара. Доступно только авторизованным."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        """После сохранения возвращаемся на карточку этого же товара (адрес зависит от pk)."""
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара с подтверждением. Доступно только авторизованным."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")


class ContactsView(FormView):
    """Страница контактов с формой обратной связи."""

    template_name = "catalog/contacts.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("catalog:contacts")

    def form_valid(self, form):
        """При валидной форме — сохранить обращение, напечатать его в консоль и показать сообщение об успехе."""
        feedback = form.save()
        print("Получено сообщение с формы обратной связи:")
        print(f"  Имя: {feedback.name}")
        print(f"  Телефон: {feedback.phone}")
        print(f"  Сообщение: {feedback.message}")
        messages.success(self.request, "Спасибо! Ваше сообщение отправлено.")
        return super().form_valid(form)
