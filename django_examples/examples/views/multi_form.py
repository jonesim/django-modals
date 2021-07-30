import datetime
from django_modals.widgets.select2 import Select2
from django_modals.view_mixins import MultiForm

from show_src_code.modals import MultiFormView
from django_modals.fields import FieldEx
from crispy_forms.layout import HTML
from .views import MainMenuTemplateView
from examples.models import Company, Person


class MultiFormExampleView(MainMenuTemplateView):

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'button_menu.html', ).add_items(
            ('multi_form_modal,-', 'Multi Form'),
        )


class ModalCompanyPerson(MultiFormView):

    modal_title = 'Multi form example'
    forms = [
        MultiForm(Company, ['name']),
        MultiForm(Person, ['title', 'first_name', 'surname']),
        MultiForm(Person, [('title', {'widget': Select2, 'required': False}), 'first_name', 'surname']),
    ]

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        if form.form_id == 'CompanyForm':
            message = 'This is the company form'
        elif form.form_id == 'PersonForm':
            message = 'This is the 1st person form'
        elif form.form_id == 'PersonForm_1':
            message = 'This is the 2nd person form'
        else:
            message = ''
        # noinspection PyTypeChecker
        return [HTML(f'<p>{message}</p>')] + [FieldEx(f) for f in form.fields]

    def forms_valid(self, valid_forms):
        company = valid_forms['CompanyForm'].save()
        valid_forms['PersonForm'].instance.company = company
        valid_forms['PersonForm'].instance.date_entered = datetime.date.today()
        valid_forms['PersonForm'].save()
        return self.command_response('reload')
