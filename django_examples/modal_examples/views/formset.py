from django.forms import TextInput
from django_datatables.datatables import DatatableView
from modal_examples.models import Company, Note, CompanyColour

from django_modals.widgets.colour_picker import ColourPickerWidget
from .views import MainMenu

from django_modals.datatables import DeleteColumn, EditColumn
from django_modals.modals import ModelFormModalFormSet
from django_modals.url_helper import get_urls
from django_modals.widgets.widgets import Toggle


class FormsetView(MainMenu, DatatableView):

    model = Company
    template_name = 'example_views/formset.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('formset_modal,-', 'Add'),
            ('formset_multi_modal,-', 'Add Multi'),

        )

    @staticmethod
    def setup_table(table):
        table.add_columns('id',
                          'name',
                          'active',
                          DeleteColumn('company_modal'),
                          EditColumn('formset_modal'),
                          EditColumn('formset_multi_modal', button_text='Multi edit')
                          )

        table.ajax_data = False


class SmallInputWidget(TextInput):
    crispy_kwargs = {'field_class': 'col-sm-3',
                     'input_size': 'input-group-sm'}


class CurrencyWidget2(TextInput):

    @property
    def crispy_kwargs(self):
        return {'prepended_text': '$',
                'field_class': 'col-md-3 input-group-sm',
                'input_size': 'input-group-sm'}


class FormsetCompanyModal(ModelFormModalFormSet):

    formset_model = Note
    model = Company
    form_fields = ['name', 'active', 'importance']
    widgets = {'active': Toggle}
    formset_fields = ['notes',
                      ('date', {'wrapper_class': 'col-2'}),
                      'completed',
                      ('price', {'wrapper_class': 'col-2'}),
                      'colour']

    formset_widgets = {'completed': Toggle,
                       'notes': SmallInputWidget,
                       'price': CurrencyWidget2,
                       'colour': ColourPickerWidget}

    def get_form_set_query(self):
        return self.object.note_set.all()


class FormsetCompanyMultiModal(ModelFormModalFormSet):
    number_of_formsets = 2
    formset_model_1 = Note
    model = Company
    form_fields = ['name', 'active', 'importance']
    widgets = {'active': Toggle}
    formset_fields_1 = ['notes',
                        ('date', {'wrapper_class': 'col-2'}),
                        'completed',
                        ('price', {'wrapper_class': 'col-2'}),
                        'colour']

    formset_widgets_1 = {'completed': Toggle,
                         'notes': SmallInputWidget,
                         'price': CurrencyWidget2,
                         'colour': ColourPickerWidget}

    formset_title_1 = 'Notes'

    formset_model_2 = CompanyColour
    formset_fields_2 = ['colour',
                        ]

    formset_widgets_2 = {'colour': ColourPickerWidget}
    formset_title_2 = 'Company Colours'

    def get_form_set_query_1(self):
        return self.object.note_set.all()

    def get_form_set_query_2(self):
        return self.object.companycolour_set.all()


urlpatterns = get_urls(__name__)
