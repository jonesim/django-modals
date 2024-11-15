from crispy_forms.layout import Div, HTML
from django.urls import reverse

from django_modals.helper import show_modal
from django_modals.modals import TemplateModal, ModelFormModal
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


class DatatablesNestedModal(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        companies_url = show_modal('datatable_company_modal', href=True)
        datatables_nested_modal_url = show_modal('datatables_nested_modal', href=True)

        return ['name',
                'active',
                Div(HTML(f'<a href="{companies_url}">Companies</a> '), css_class='text-center'),
                Div(HTML(f'<a href="{datatables_nested_modal_url}">self</a> '), css_class='text-center')]


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
