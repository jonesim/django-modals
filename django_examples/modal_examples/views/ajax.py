from django_modals.messages import AjaxMessagesMixin
from .views import MainMenuTemplateView


class AjaxExamples(AjaxMessagesMixin, MainMenuTemplateView):

    template_name = 'example_views/ajax.html'

    def button_info(self, **_kwargs):
        return self.ajax_message('This can give information')

    def button_warning(self, **_kwargs):
        return self.warning_message('No Files')

    def button_error(self, **_kwargs):
        return self.error_message('This is a really bad error message which also has a long description')
