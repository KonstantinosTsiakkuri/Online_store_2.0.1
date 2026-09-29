"""Контроллеры приложения blog. Полный CRUD на классовых контроллерах (CBV)."""

from django.db.models import F
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from blog.models import BlogPost


class BlogPostListView(ListView):
    """Список статей блога."""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        """В списке показываем только опубликованные статьи."""
        return super().get_queryset().filter(is_published=True)


class BlogPostDetailView(DetailView):
    """Детальная страница статьи. При каждом открытии увеличивает счётчик просмотров."""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        """Отдать статью и увеличить её счётчик просмотров ровно на 1 в базе данных."""
        post = super().get_object(queryset)
        # F-выражение считает "views_count + 1" на стороне БД — так параллельные
        # запросы не затирают прирост друг друга, как это было бы при чтении
        # значения в Python и обратной записи.
        post.views_count = F("views_count") + 1
        post.save(update_fields=["views_count"])
        post.refresh_from_db(fields=["views_count"])
        return post


class BlogPostCreateView(CreateView):
    """Создание новой статьи."""

    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ("title", "content", "preview", "is_published")
    success_url = reverse_lazy("blog:post_list")


class BlogPostUpdateView(UpdateView):
    """Редактирование существующей статьи."""

    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ("title", "content", "preview", "is_published")

    def get_success_url(self):
        """
        После сохранения переходим на страницу именно этой статьи.

        Обычный статический success_url тут не подходит: адрес детальной
        страницы зависит от pk конкретного объекта, а атрибут класса
        вычисляется один раз при загрузке кода, когда объекта ещё нет.
        get_success_url вызывается уже после сохранения формы, когда
        self.object — сохранённая статья с известным pk.
        """
        return reverse("blog:post_detail", args=[self.object.pk])


class BlogPostDeleteView(DeleteView):
    """Удаление статьи с подтверждением."""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
