from django_menus.menu import MenuItem
from show_src_code.modals import ModelFormModal, BaseSourceCodeModal

from django_modals.helper import modal_delete_javascript
from django_modals.processes import PERMISSION_OFF, PROCESS_VIEW, PROCESS_EDIT_DELETE, PROCESS_EDIT

from modal_examples.models import Company
from .views import MainMenuTemplateView


class CrudExamples(MainMenuTemplateView):
    template_name = 'example_views/crud.html'

    def crud_menu(self):
        self.add_menu('modals', 'buttons', ).add_items(
            ('company_modal,-', 'Create'),
            (f'company_modal,pk-{self.company.id}-modal-view', 'View'),
            (f'company_modal,pk-{self.company.id}-modal-viewedit', 'View/Edit'),
            (f'company_modal,pk-{self.company.id}-modal-edit', 'Edit'),
            (f'company_modal,pk-{self.company.id}-modal-editdelete', 'Edit/Delete'),
            (modal_delete_javascript('company_modal', self.company.id), 'Delete', MenuItem.JAVASCRIPT),
        )

    def different_views(self):
        self.add_menu('view_configured', 'buttons', ).add_items(
            (f'crud_read,{self.company.id}', 'View'),
            (f'crud_edit,{self.company.id}', 'Edit'),
            (f'crud_edit_delete,{self.company.id}', 'Edit/Delete'),
        )

    def setup_menu(self):
        super().setup_menu()
        self.company = Company.objects.first()
        self.crud_menu()
        self.different_views()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.company.id
        context['source1'] = self.setup_menu
        return context


class ModalCompanyForm(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']
    permission_delete = PERMISSION_OFF

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CrudRead(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']
    process = PROCESS_VIEW


class CrudEdit(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']
    process = PROCESS_EDIT


class CrudEditDelete(ModelFormModal):

    model = Company
    form_fields = ['name', 'active']
    process = PROCESS_EDIT_DELETE
    permission_delete = PERMISSION_OFF


class SourceCodeModal(BaseSourceCodeModal):
    code = {
        'crud_menu': CrudExamples.crud_menu,
        'crud_view_menu': CrudExamples.different_views,
    }
