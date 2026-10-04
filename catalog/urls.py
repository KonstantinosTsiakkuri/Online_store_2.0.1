"""Маршруты приложения catalog."""

from django.urls import path

from catalog import views

app_name = "catalog"

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("contacts/", views.contacts, name="contacts"),
]
