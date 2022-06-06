import json
from django.forms import Select, ChoiceField, TypedChoiceField, SelectMultiple, MultipleChoiceField
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.safestring import mark_safe


def widget_attrs(widget):
    return ''.join([f' {n}' if v is True else f' {n}={v}' for n, v in widget['attrs'].items() if v is not False])


def select2_ajax_result(results):
    return JsonResponse({'results': [{'id': r[0], 'text': r[1]} for r in results]})


class SelectGroupMixin:

    def get_context(self, name, value, attrs):
        # noinspection PyUnresolvedReferences
        context = super().get_context(name, value, attrs)
        options = []
        for group_name, group_choices, group_index in context['widget']['optgroups']:
            if group_name:
                options.append(f'<optgroup label="{group_name}">')
            for option in group_choices:
                options.append(f'<option value="{option["value"]}"{widget_attrs(option)}>{option["label"]}</option>')
            if group_name:
                options.append('</optgroup>')
        context['options_str'] = ''.join(options)
        return context


def add_width(style):
    no_space_style = style.replace(' ', '')
    if not style:
        return 'width:100%'
    elif not no_space_style.startswith('width:') and ';width:' not in no_space_style:
        return style + ';width:100%'
    return style


class Select2(SelectGroupMixin, Select):
    template_name = 'django_modals/widgets/select2.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['style'] = add_width(context['widget']['attrs'].get('style', ''))
        if hasattr(self, 'select_data'):
            context['widget']['select_data'] = mark_safe(json.dumps(self.select_data))
        return context


class TypedSelect2(SelectGroupMixin, TypedChoiceField):
    template_name = 'django_modals/widgets/select2.html'


class Select2Multiple(SelectGroupMixin, SelectMultiple):
    template_name = 'django_modals/widgets/select2.html'
    new_marker = 'new:'

    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags', False)
        if tags:
            kwargs.setdefault('attrs', {}).update({'new_marker': self.new_marker, 'tags': True})
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['style'] = add_width(context['widget']['attrs'].get('style', ''))
        return context


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
            model_object = self.model.objects.get(pk=value)
            self.choices = ((model_object.id, str(model_object)),)
        return super().prepare_value(value)


class MultipleChoiceFieldAddValues(MultipleChoiceField):

    widget = Select2Multiple

    def valid_value(self, value):
        return True

    def clean(self, value):
        return_data = {'existing': [], 'new': []}
        for v in value:
            if v.startswith(Select2Multiple.new_marker):
                return_data['new'].append(v[len(Select2Multiple.new_marker):])
            else:
                return_data['existing'].append(v)
        return return_data

    def widget_attrs(self, widget):
        return {'new_marker': Select2Multiple.new_marker, 'tags': True}


class ChoiceFieldAddValues(ChoiceField):

    new_marker = 'new:'

    def __init__(self, choices=None, model=None, display_field=None, widget=None, **kwargs):
        if model and display_field:
            choices = model.objects.values_list('id', display_field)
        if not widget:
            self.widget = Select2(attrs={'new_marker': 'new:', 'tags': True})
        super().__init__(choices=choices, **kwargs)

    def clean(self, value):
        return value

    def bound_data(self, data, initial):
        if data and self.new_data(data):
            if self.choices[-1][1] != self.new_data(data):
                self.choices.append((data, self.new_data(data)))
        return super().bound_data(data, initial)

    @classmethod
    def new_data(cls, value):
        if value.startswith(cls.new_marker):
            return value[len(cls.new_marker):]
