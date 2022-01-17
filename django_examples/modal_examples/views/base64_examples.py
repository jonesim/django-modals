from django_menus.menu import MenuItem

from django_modals.helper import show_modal, base64_json
from .views import MainMenuTemplateView
from show_src_code.modals import Modal


class B64(MainMenuTemplateView):

    template_name = 'example_views/basic.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            (show_modal('base64_modal', base64={'item': 'test chars |-`/~1Ⓒ'}, href=True), 'Data sent with base64',
             MenuItem.HREF),
            (f"base64_modal,{base64_json({'item': 'test chars |-`/~1Ⓒ'})}"),
        )


class B64Modal(Modal):
    button_container_class = 'text-center'

    def modal_content(self):
        return f'Slug obtained from base64 dictionary<br> {self.slug.__str__()}'
