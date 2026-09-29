"""Формы приложения catalog."""

from django import forms

from catalog.models import Feedback


class FeedbackForm(forms.ModelForm):
    """Форма обратной связи. Все поля обязательны."""

    class Meta:
        model = Feedback
        fields = ("name", "phone", "message")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Иван Иванов"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7 900 000-00-00"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Текст сообщения"}),
        }
