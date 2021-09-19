from show_src_code.modals import ModelFormModal
from modal_examples.models import Company
from .views import MainMenu


class NoModal(MainMenu, ModelFormModal):
    menu_config = '{}'
    template_name = 'example_views/no_modal.html'
    modal_mode = False
    model = Company
    form_fields = ['name', 'active']
