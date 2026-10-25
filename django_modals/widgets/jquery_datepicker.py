from django.forms import DateInput
from ..fields import FieldEx, LegacyWidgetAttributes


class DatePicker(LegacyWidgetAttributes, DateInput):
    template_name = 'django_modals/widgets/datepicker.html'
    modal_field_class = FieldEx
    modal_kwargs = {'appended_text': '<i class="fas fa-calendar-alt fa-fw"></i>', 'input_size': 'input-group-sm'}
