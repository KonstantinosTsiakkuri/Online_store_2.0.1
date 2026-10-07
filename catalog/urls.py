"""Маршруты приложения catalog."""

from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="home"),
    path("category/<int:pk>/", views.CategoryProductsView.as_view(), name="category_products"),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    # Страница товара кешируется целиком. cache_page учитывает Vary: Cookie, поэтому
    # у каждой сессии своя копия (кнопки и меню зависят от пользователя).
    path(
        "products/<int:pk>/",
        cache_page(settings.CACHE_TTL_PRODUCT_DETAIL)(views.ProductDetailView.as_view()),
        name="product_detail",
    ),
    path("products/<int:pk>/update/", views.ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
]
