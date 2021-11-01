from django.core.exceptions import ValidationError
from modal_examples.models import Company
from show_src_code.modals import ModelFormModal

from django_modals.processes import PROCESS_EDIT
from .views import MainMenuTemplateView


class ValidationExamples(MainMenuTemplateView):
    template_name = 'example_views/validation.html'


class ValidationClean(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']
    process = PROCESS_EDIT

    def clean(self, form, cleaned_data):
        if cleaned_data['name'] == 'NA':
            raise ValidationError("Can't enter NA")
