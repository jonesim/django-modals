from django_datatables.datatables import DatatableView
from modal_examples.models import Company, Note


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

        )

    @staticmethod
    def setup_table(table):
        table.add_columns('id',
                          'name',
                          'active',
                          DeleteColumn('company_modal'),
                          EditColumn('formset_modal')
                          )

        table.ajax_data = False


class FormsetCompanyModal(ModelFormModalFormSet):

    formset_model = Note
    model = Company
    form_fields = ['name', 'active']
    widgets = {'active': Toggle}
    formset_fields = ['notes', 'date', 'completed']
    formset_widgets = {'completed': Toggle}

    def get_form_set_query(self):
        return self.object.note_set.all()


urlpatterns = get_urls(__name__)
