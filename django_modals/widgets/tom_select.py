import json
from django.forms import Select, TypedChoiceField, SelectMultiple
from django.utils.safestring import mark_safe

# Shared, library-agnostic helpers reused from the Select2 implementation.
from django_modals.widgets.select2 import SelectGroupMixin, add_width, widget_attrs, select2_ajax_result  # noqa: F401


class TomSelect(SelectGroupMixin, Select):
    template_name = 'django_modals/widgets/tom_select.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['style'] = add_width(context['widget']['attrs'].get('style', ''))
        if hasattr(self, 'select_data'):
            context['widget']['select_data'] = mark_safe(json.dumps(self.select_data))
        return context


class TypedTomSelect(SelectGroupMixin, TypedChoiceField):
    template_name = 'django_modals/widgets/tom_select.html'


class TomSelectMultiple(SelectGroupMixin, SelectMultiple):
    template_name = 'django_modals/widgets/tom_select.html'
    new_marker = 'new:'

    def __init__(self, *args, **kwargs):
        tags = kwargs.pop('tags', False)
        if tags:
            kwargs.setdefault('attrs', {}).update({'new_marker': self.new_marker, 'tags': True})
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['style'] = add_width(context['widget']['attrs'].get('style', ''))
        if hasattr(self, 'select_data'):
            context['widget']['select_data'] = mark_safe(json.dumps(self.select_data))
        return context
