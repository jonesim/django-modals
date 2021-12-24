import os
from django.forms.fields import FileField
from crispy_forms.layout import HTML

from django_modals.modal_upload import ModalAjaxFileMixin
from django_modals.forms import CrispyForm
from django_modals.modals import FormModal
from django_modals.helper import progress_bar

from .views import MainMenuTemplateView


class Upload(ModalAjaxFileMixin, MainMenuTemplateView):

    template_name = 'example_views/upload.html'

    @staticmethod
    def upload_files(filename, _size, file, **_kwargs):
        path = '/media/' + filename
        with open(path, 'wb+') as destination:
            destination.write(file.read())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = os.listdir('/media/')
        return context


class UploadForm(CrispyForm):
    File = FileField()

    class Meta:
        progress_bar = True

    def post_init(self, *args, **kwargs):
        return ['File', HTML(progress_bar())]


class UploadModal(FormModal):
    form_class = UploadForm
    modal_title = 'Upload Form'

    # Due to timeout in modals.js this will not upload large files

    def form_valid(self, form):
        print(form.cleaned_data)
