from crispy_forms.layout import HTML
from django_datatables.datatables import DatatableView

from django_modals.datatables import EditColumn
from django_modals.modals import MultiForm, MultiFormFormSet, MultiFormModal
from django_modals.widgets.colour_picker import ColourPickerWidget
from django_modals.widgets.jquery_datepicker import DatePicker
from django_modals.widgets.widgets import Toggle
from modal_examples.models import Company, Note
from modal_examples.views.formset import SmallInputWidget, CurrencyWidget2
from modal_examples.views.views import MainMenu


class MultiFormFormsetView(MainMenu, DatatableView):

    model = Company
    template_name = 'example_views/formset.html'
    menu_display = 'MF Formset'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(('mf_formset_modal,-', 'Add'),
                                                       ('mf_formset_modal,table-true', 'Add Table'))

    @staticmethod
    def setup_table(table):
        table.add_columns('id',
                          'name',
                          'active',
                          EditColumn('mf_formset_modal'),
                          EditColumn('mf_formset_modal', modal_args=('table-true',)),
                          )
        table.ajax_data = False

class MultiFormFormsetCompanyModal(MultiFormModal):

    modal_title = 'Multi Form Formset'
    @property
    def forms(self):
        return [MultiForm(Company, ['name', 'active', 'importance'], pk=self.slug.get('pk')),
                *MultiFormFormSet(self, model=Note, fields=['notes', HTML('g'),  'date' ,'colour', 'completed', 'price'],
                                  parent_id=self.slug.get('pk'), table=self.slug.get('table', False),
                                  parent_model=Company,
                                  widgets={'date': DatePicker,
                                           'colour': ColourPickerWidget,
                                           'completed': Toggle,
                                           'notes': SmallInputWidget,
                                           'price': CurrencyWidget2,}).get_set_forms(self.form_data),
                ]
