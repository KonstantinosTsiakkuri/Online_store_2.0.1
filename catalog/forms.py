"""Формы приложения catalog."""

from django import forms

from catalog.models import Feedback, Product

# Слова, которые нельзя использовать в названии и описании товара
FORBIDDEN_WORDS = (
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
)


def find_forbidden_word(value):
    """Вернуть первое найденное запрещённое слово или None. Сравнение без учёта регистра."""
    if not value:
        return None
    lowered = value.lower()
    for word in FORBIDDEN_WORDS:
        if word in lowered:
            return word
    return None


class StyledFormMixin:
    """Проставляет Bootstrap-классы всем полям формы в зависимости от типа виджета."""

    def _apply_bootstrap_styles(self):
        """Добавить нужный CSS-класс каждому виджету, не затирая уже заданные классы."""
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = "form-select"
            else:
                css_class = "form-control"
            existing = widget.attrs.get("class", "")
            if css_class not in existing.split():
                widget.attrs["class"] = f"{existing} {css_class}".strip()


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


class ProductForm(StyledFormMixin, forms.ModelForm):
    """
    Форма создания и редактирования товара с проверкой на запрещённые слова и отрицательную цену.

    Поля owner и is_published сюда намеренно не входят: владелец выставляется
    автоматически во вьюхе при создании, а публикацией управляет отдельная
    ProductModeratorForm — ни то, ни другое пользователь не должен редактировать сам.
    """

    class Meta:
        model = Product
        fields = ("name", "description", "image", "category", "price")

    def __init__(self, *args, **kwargs):
        """Навесить Bootstrap-стили на все поля формы."""
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_styles()

    def clean_name(self):
        """Запретить использование запрещённых слов в названии товара."""
        name = self.cleaned_data.get("name")
        word = find_forbidden_word(name)
        if word:
            raise forms.ValidationError(f"Название не может содержать слово «{word}». Измените название товара.")
        return name

    def clean_description(self):
        """Запретить использование запрещённых слов в описании товара."""
        description = self.cleaned_data.get("description")
        word = find_forbidden_word(description)
        if word:
            raise forms.ValidationError(f"Описание не может содержать слово «{word}». Измените описание товара.")
        return description

    def clean_price(self):
        """Не пропускать отрицательную цену."""
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной. Укажите цену от 0 и выше.")
        return price


class ProductModeratorForm(StyledFormMixin, forms.ModelForm):
    """Урезанная форма для модераторов: позволяет только снять товар с публикации или опубликовать его."""

    class Meta:
        model = Product
        fields = ("is_published",)

    def __init__(self, *args, **kwargs):
        """Навесить Bootstrap-стили на единственное поле формы."""
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_styles()
