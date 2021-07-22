import json
from django.forms import Select, ChoiceField, TypedChoiceField, SelectMultiple, MultipleChoiceField
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


class Select2(Select):
    template_name = 'django_modals/widgets/select2.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if not self.attrs.get('ajax') and hasattr(self, 'select_data'):
            context['widget']['select_data'] = mark_safe(json.dumps(self.select_data))
        return context


class TypedSelect2(TypedChoiceField):
    template_name = 'django_modals/widgets/select2.html'


class Select2Multiple(SelectMultiple):
    template_name = 'django_modals/widgets/select2.html'
    new_marker = 'new:'

    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags', False)
        if tags:
            kwargs.setdefault('attrs', {}).update({'new_marker': self.new_marker, 'tags': True})
        super().__init__(*args, **kwargs)


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


class MultipleChoiceFieldAddValues(MultipleChoiceField):

    widget = Select2Multiple

    def valid_value(self, value):
        return True

    def clean(self, value):
        return_data = {'existing': [],'new': []}
        for v in value:
            if v.startswith(Select2Multiple.new_marker):
                return_data['new'].append(v[len(Select2Multiple.new_marker):])
            else:
                return_data['existing'].append(v)
        return return_data

    def widget_attrs(self, widget):
        return {'new_marker': Select2Multiple.new_marker, 'tags': True}
