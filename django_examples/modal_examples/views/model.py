from urllib.parse import quote
from django.urls import reverse
from django.forms.fields import CharField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from crispy_forms.layout import Field, HTML

from django_datatables.datatables import DatatableView
import django_modals.modals as modals
from django_modals.forms import ModelCrispyForm
from django_modals.widgets.select2 import Select2
from django_modals.processes import PERMISSION_ON, PERMISSION_OFF, PROCESS_CREATE
from django_modals.datatables import EditColumn, DeleteColumn
from django_modals.url_helper import get_urls
from django_modals.mixins import ScratchPad
from modal_examples.models import Company, Person

from show_src_code.modals import ModelFormModal, MultiFormModal
from .views import MainMenu


class ModelExamples(MainMenu, DatatableView):

    model = Company
    template_name = 'example_views/model.html'

    @staticmethod
    def setup_company_table(table):
        table.add_columns('id', 'name', 'active', 'Tags', DeleteColumn('company_modal'),
                          EditColumn('company_people_modal'))

        table.ajax_data = False

    def add_tables(self):
        self.add_table('company_table', model=Company)
        self.add_table('people_table', model=Person)

    @staticmethod
    def setup_people_table(table):
        table.add_columns(
            'id',
            'first_name',
            'surname',
            ('company__name', {'title': 'Company Name'}),
            DeleteColumn('company_modal', css_class='text-secondary text-center'),
            EditColumn('person_nocompany_modal')
        )
        table.ajax_data = False

    def setup_menu(self):
        super().setup_menu()

        self.add_menu('modals', 'buttons', ).add_items(
            (f'company_modal,name-{quote("Prefilled Name")}', 'Company Create pre filled name'),
            ('extra_field_modal,readonly-True', 'Company Extra field'),
            ('company_people_modal,-', 'Company/People modal'),

        )
        self.add_menu('query_set', 'buttons', ).add_items(
            (f'person_filter,filter-first', 'Person- company queryset 1st half'),
            (f'person_filter,filter-second', 'Person- company queryset 2nd half'),

        )
        self.add_menu('separate_form', 'buttons', ).add_items(
            ('separate_form_modal,-', 'Separate Form')
        )
        self.add_menu('field_setup', 'buttons', ).add_items(
            ('PersonFieldSetup,-', 'Field Setup'),
            ('PersonViewSetup,-', 'View Setup'),
        )


class ModalCompanyForm(ScratchPad, ModelFormModal):

    model = Company
    form_fields = ['name', 'active']

    permission_delete = PERMISSION_OFF

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



from django.forms.widgets import TextInput


class CurrencyWidget(TextInput):

    def render(self, name, value, attrs=None, renderer=None):
        if value:
            value = str(int(value)/100.0)
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        return float(data['name']) * 100



class ModalCompanyFormExtraField(ModelFormModal):

    model = Company
    modal_title = ['New', 'Edit']
    form_fields = [('name', {'widget': CurrencyWidget}),]

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['extra'] = CharField()
        form.fields['extra'].help_text = 'Field added in form_setup'

    def form_valid(self, form):
        print(form.cleaned_data)

class ModalCompanyFormPeople(ModelFormModal):
    model = Company
    form_fields = ['name', 'active']
    permission_delete = PERMISSION_ON

    @property
    def extra_context(self):
        if self.process == PROCESS_CREATE:
            return {'contents':
                    mark_safe('After company is created the same form will allow the adding of people<br><br>')}

    @property
    def delete_message(self):
        return f'Are you sure you want to delete id:{self.object.id}  {self.object.name} ?'

    def form_setup(self, form, *_args, **_kwargs):
        if self.object.id:
            form.modal_title = (f'Edit Company  <a href="{reverse("company", args=(self.object.id,))}">'
                                f'{self.object.name}</a>')
        return Field(*form.Meta.fields), HTML(render_to_string('modal_examples/people.html', {'company': form.instance}))

    def form_valid(self, form):
        if not self.object.id:
            form.save()
            self.request.path = reverse('company_people_modal', kwargs={'slug': self.object.id})
            self.add_command('overwrite_modal', html=self.get(self.request, pk=self.object.id).rendered_content)
        return super().form_valid(form)


class ModalPersonForm(ModelFormModal):

    model = Person
    modal_title = ['New Person', 'Edit Person']
    form_fields = ['title', 'company', 'first_name', 'surname']

    widgets = {'title': Select2, 'company': Select2}

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['company'].queryset = Company.objects.filter(id__gt=1)


class CompanyForm(ModelCrispyForm):

    class Meta:
        model = Company
        fields = ['name']


class ModalCompanySeparateForm(ModelFormModal):
    form_class = CompanyForm


class ModalCompanyPerson(MultiFormModal):

    modal_title = 'Multi form example'
    forms = [
        modals.MultiForm(Company, ['name']),
        modals.MultiForm(Person, ['title', 'first_name', 'surname']),
    ]

    def forms_valid(self, valid_forms):
        company = valid_forms['CompanyForm'].save()
        valid_forms['PersonForm'].instance.company = company
        valid_forms['PersonForm'].save()
        return self.command_response('reload')


# Used in table as company already selected
class ModalPersonNoCompanyForm(ModelFormModal):

    model = Person
    form_fields = ['title', 'first_name', 'surname']
    widgets = {'title': Select2}
    permission_delete = PERMISSION_OFF


class ModalPersonFilter(ModelFormModal):

    model = Person
    form_fields = ['title', 'first_name', 'surname', 'company']
    widgets = {'title': Select2, 'company': Select2}

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        no_companies = Company.objects.count()
        if form.slug['filter'] == 'first':
            form.fields['company'].queryset = Company.objects.all()[:no_companies//2]
            form.fields['company'].help_text = 'Company only shows <b>first</b> half of companies'
        else:
            form.fields['company'].queryset = Company.objects.all()[no_companies//2:]
            form.fields['company'].help_text = 'Company only shows <b>second</b> half of companies'


class PersonFieldSetup(ModelFormModal):

    model = Person

    form_fields = [
        ('title', {'label': 'Title (field)', 'help_text': 'Title help text from field definition'}),
        ('first_name', {'placeholder': 'Field placeholder'}),
        ('surname', {'error_messages': {'required': 'REQUIRED - field message'},
                     'help_text': 'Different error message'}),
        ('company', {'widget': Select2, 'help_text': 'Widget (Select2) set in field definition'})
    ]


class PersonViewSetup(ModelFormModal):

    model = Person

    labels = {'first_name': 'First Name (View)'}
    help_texts = {'surname': 'Surname help from view'}
    widgets = {'title': Select2}
    error_messages = {'surname': {'required': 'ERROR REQUIRED'}}

    form_fields = [
        'title',
        'first_name',
        'surname',
        'company',
    ]

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['title'].widget.attrs = {'placeholder': 'Title - placeholder set in form setup'}


urlpatterns = get_urls(__name__)
