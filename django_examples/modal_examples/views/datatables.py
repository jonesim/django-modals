from django_modals.modals import TemplateModal
from django_modals.modals.datatables import DatatableModal
from modal_examples.models import Company
from .views import MainMenu
from django_datatables.datatables import DatatableView


class DatatablesView(MainMenu, DatatableView):
    model = Company
    template_name = 'example_views/datatables.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            'datatable_company_modal', 'datatables_nested_modal')

    @staticmethod
    def setup_table(table):
        table.add_columns('id',
                          'name',
                          'active',
                          )


class DatatablesNestedModal(TemplateModal):

    modal_template = 'modal_examples/datatable_nested.html'

    def modal_context(self):
        return {'view': 'From view'}

    def button_ajax_command(self, **_kwargs):
        return self.command_response('message', text='Ajax button pressed')


class DisplayCompanyModal(DatatableModal):

    button_container_class = 'text-center'
    modal_title = 'Display Companies'
    model = Company

    def setup_table(self, table):

        table.add_columns(
            '.id',
            'name',
            'active',
            'people',
        )
        table.table_options['language'] = {'emptyTable': 'No companies found'}
