"""Маршруты приложения blog."""

from django.urls import path

from blog import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="post_list"),
    path("<int:pk>/", views.BlogPostDetailView.as_view(), name="post_detail"),
    path("create/", views.BlogPostCreateView.as_view(), name="post_create"),
    path("<int:pk>/update/", views.BlogPostUpdateView.as_view(), name="post_update"),
    path("<int:pk>/delete/", views.BlogPostDeleteView.as_view(), name="post_delete"),
]
