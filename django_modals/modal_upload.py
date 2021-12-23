from ajax_helpers.mixins import AjaxFileUploadMixin

from django_modals.modals import Modal
from django_modals.helper import ajax_modal_replace
from .helper import progress_bar
from .messages import AjaxMessagesMixin


class UploadModal(Modal):

    def get_modal_buttons(self):
        return []

    def modal_content(self):
        progress_bars = []
        for c, f in enumerate(self.kwargs['files']):
            progress_bars.append(f'<div>Uploading file: <b>{f["name"]}</b></div>' + progress_bar(c))
        progress_bars.append('''<h5 class='p-3 w-100 text-center' id="upload_message">&nbsp;</h4>''')
        return ''.join(progress_bars)


class ModalAjaxFileMixin(AjaxMessagesMixin, AjaxFileUploadMixin):
    single_progress_bar = False

    def upload_completed(self):
        self.add_command('html', selector='#upload_message', html='Upload Complete')
        self.add_command('delay', time=1800)
        return self.command_response('reload')

    def start_upload_files(self, **kwargs):
        kwargs['files'] = [f for f in kwargs['files'] if f['size'] > 0]
        if len(kwargs['files']) == 0:
            return self.error_message('No files selected')
        self.response_commands.append(
            ajax_modal_replace(self.request, modal_class=UploadModal, ajax_function='modal_html', files=kwargs['files'])
        )
        return self.command_response('upload_file', **self.upload_file_command(0, **kwargs))
