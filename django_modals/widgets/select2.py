from django.forms import Select, ChoiceField, TypedChoiceField, SelectMultiple
from django.core.exceptions import ValidationError

class Select2(Select):
    template_name = 'widgets/select2.html'


class TypedSelect2(TypedChoiceField):
    template_name = 'widgets/select2.html'


class Select2Multiple(SelectMultiple):
    template_name = 'widgets/select2.html'


class ModelSelect2ChoiceField(ChoiceField):

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')
        return value

    def to_python(self, value):
        if value:
            return self.model.objects.get(pk=value)

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        if 'widget' not in kwargs:
            kwargs['widget'] = Select2(attrs={'ajax': True})
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        if value:
            object = self.model.objects.get(pk=value)
            self.choices = ((object.id, str(object)),)
        return super().prepare_value(value)
