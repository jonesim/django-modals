from django.core.exceptions import ValidationError
from modal_examples.models import Company
from show_src_code.modals import ModelFormModal

from django_modals.processes import PROCESS_EDIT
from .views import MainMenuTemplateView


class ValidationExamples(MainMenuTemplateView):
    template_name = 'example_views/validation.html'


class ValidationClean(ModelFormModal):

    model = Company
    form_fields = [('name', {'help_text': "Type na or NA"}), 'active']
    process = PROCESS_EDIT

    def clean(self, form, cleaned_data):
        if cleaned_data.get('name') == 'NA':
            raise ValidationError("This is a form error")
        if cleaned_data.get('name') == 'na':
            form.add_error('name', "This is a field error")
