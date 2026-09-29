"""Контроллеры приложения catalog."""

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView

from catalog.forms import FeedbackForm
from catalog.models import Product


class ProductListView(ListView):
    """Главная страница: список всех товаров из базы."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"


class ProductDetailView(DetailView):
    """Детальная страница товара. Несуществующий pk даёт 404 автоматически."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


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
