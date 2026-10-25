from django.forms import CheckboxInput, Textarea
from ..fields import LegacyWidgetAttributes


class Toggle(LegacyWidgetAttributes, CheckboxInput):
    template_name = 'django_modals/widgets/toggle.html'
    modal_kwargs = {'template': 'django_modals/forms/bootstrap4/checkbox.html', 'field_class': 'col-6 input-group-sm'}


class TinyMCE(LegacyWidgetAttributes, Textarea):
    template_name = 'django_modals/widgets/tinymce.html'
    modal_kwargs = {'label_class': 'col-3 col-form-label-sm', 'field_class': 'col-12 input-group-sm'}
