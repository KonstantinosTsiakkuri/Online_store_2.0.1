"""Контроллеры приложения catalog."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from catalog.forms import FeedbackForm, ProductForm, ProductModeratorForm
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
    """Создание нового товара. Доступно только авторизованным; владельцем становится автор."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        """Сохранить товар с owner = текущий пользователь (поля owner в форме нет, его задаём здесь)."""
        product = form.save(commit=False)
        product.owner = self.request.user
        product.save()
        self.object = product
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """
        После создания переходим на карточку нового товара.

        Статический success_url тут не подходит: адрес зависит от pk,
        который появляется только после сохранения объекта.
        """
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование товара.

    Какую форму показать, зависит от того, кто смотрит: владелец получает полную
    форму, модератор (право can_unpublish_product) — только переключатель публикации,
    остальным редактирование запрещено вовсе.
    """

    model = Product
    template_name = "catalog/product_form.html"

    def get_form_class(self):
        """Выбрать форму по роли текущего пользователя относительно товара."""
        # self.object уже установлен к этому моменту: UpdateView вызывает get_object()
        # в своих get()/post() до того, как добраться до get_form() -> get_form_class().
        product = self.object
        user = self.request.user
        if user == product.owner:
            return ProductForm
        if user.has_perm("catalog.can_unpublish_product"):
            return ProductModeratorForm
        raise PermissionDenied("Редактировать этот товар может только его владелец или модератор.")

    def get_success_url(self):
        """После сохранения возвращаемся на карточку этого же товара (адрес зависит от pk)."""
        return reverse("catalog:product_detail", args=[self.object.pk])


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление товара. Доступно владельцу или пользователю с правом catalog.delete_product."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")

    def get_object(self, queryset=None):
        """
        Получить товар и сразу проверить права.

        DeleteView вызывает get_object() и в get() (страница подтверждения),
        и в post() (само удаление) — одной проверки здесь достаточно на оба случая.
        """
        product = super().get_object(queryset)
        user = self.request.user
        if user != product.owner and not user.has_perm("catalog.delete_product"):
            raise PermissionDenied("Удалить этот товар может только его владелец или модератор.")
        return product


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
