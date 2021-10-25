import inspect
from django.views.generic import TemplateView
from ajax_helpers.mixins import AjaxHelpers
from django_menus.menu import MenuMixin
from show_src_code.view_mixins import DemoViewMixin


class MainMenu(DemoViewMixin, AjaxHelpers, MenuMixin):
    template_name = 'modal_examples/demo.html'

    def setup_menu(self):
        self.add_menu('main_menu').add_items(
            'basic', 'unbound', 'layout', ('crud', 'CRUD'), 'model',
            ('multi_form', 'Multi Form'), 'adaptive', 'users', 'permissions', 'widgets',
            ('no_modal,-', 'No modal'), 'upload', 'ajax', 'validation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_class'] = inspect.getmodule(self).__name__ + '.' + self.__class__.__name__
        return context


class MainMenuTemplateView(MainMenu, TemplateView):
    pass
