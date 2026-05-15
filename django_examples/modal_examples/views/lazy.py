from time import sleep

from show_src_code.modals import ModelFormModal, Modal
from modal_examples.models import Company
from django_modals.url_helper import get_urls
from .views import MainMenuTemplateView


class LazyExamples(MainMenuTemplateView):

    template_name = 'example_views/lazy.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('examples', 'buttons').add_items(
            ('LazyCompanyModal,-', 'Lazy ModelFormModal'),
            ('LazyMessageModal,-', 'Lazy simple Modal'),
        )


class LazyCompanyModal(ModelFormModal):
    lazy = True
    model = Company
    modal_title = 'Company (lazy loaded)'
    form_fields = ['name', 'active']

    def form_setup(self, form, **kwargs):
        sleep(1.5)


class LazyMessageModal(Modal):
    lazy = True
    modal_title = 'Lazy Modal'

    def modal_content(self):
        sleep(1.5)
        return 'This content was loaded lazily after the modal appeared.'


urlpatterns = get_urls(__name__)
