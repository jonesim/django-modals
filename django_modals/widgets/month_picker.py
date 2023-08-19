from django.forms.widgets import TextInput
from ..fields import FieldEx


class MonthPicker(TextInput):
    template_name = 'django_modals/widgets/month_picker.html'
    crispy_field_class = FieldEx
    crispy_kwargs = {'appended_text': '<i class="fas fa-calendar-alt fa-fw"></i>', 'input_size': 'input-group-sm'}
