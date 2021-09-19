from django.views.generic import TemplateView
from ajax_helpers.mixins import AjaxHelpers
from django_menus.menu import MenuMixin, MenuItem


class MainMenu(AjaxHelpers, MenuMixin):
    template_name = 'django_examples/demo.html'

    def setup_menu(self):
        self.add_menu('main_menu').add_items(
             #MenuItem(menu_display='Modals', dropdown=(MenuItem('example1', visible=True), 'example2')),
            'basic', 'unbound', 'layout', ('crud', 'CRUD'), 'model',
            ('multi_form', 'Multi Form'), 'adaptive', 'users', 'permissions', 'widgets', ('no_modal,-', 'No modal'))


class MainMenuTemplateView(MainMenu, TemplateView):
    pass
