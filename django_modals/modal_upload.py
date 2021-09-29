import json
from django_modals.modals import Modal
from django_modals.helper import ajax_modal_replace
from .helper import progress_bar


class UploadModal(Modal):

    def get_modal_buttons(self):
        return []

    def modal_content(self):
        progress_bars = []
        for c, f in enumerate(self.kwargs['files']):
            progress_bars.append(f'<div>Uploading file: <b>{f["name"]}</b></div>' + progress_bar(c))
        progress_bars.append('''<h5 class='p-3 w-100 text-center' id="upload_message">&nbsp;</h4>''')
        return ''.join(progress_bars)


class ModalAjaxFileMixin:
    ajax_commands = ['start_upload', 'upload']

    def upload_completed(self):
        self.add_command('html', selector='#upload_message', html='Upload Complete')
        self.add_command('delay', time=1800)
        return self.command_response('reload')

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.content_type == 'multipart/form-data' and 'ajax_modal_file' in request.FILES:
            response = request.POST.dict()
            file = self.request.FILES['ajax_modal_file']
            upload_params = json.loads(response.get('upload_params', '{}'))
            index = int(response.pop('index'))
            file_info = json.loads(response['file_info'])
            getattr(self, 'upload_' + request.POST['upload'])(file_info[index]['name'], file_info[index]['size'], file,
                                                              **upload_params)
            if len(file_info) > index + 1:
                response['upload_params'] = upload_params
                self.response_commands.append(self.upload_file_command(index + 1, **response))
                return self.command_response()
            return self.upload_completed()
        return super().post(request, *args, **kwargs)

    def start_upload_files(self, **kwargs):
        self.response_commands.append(
            ajax_modal_replace(self.request, modal_class=UploadModal, ajax_function='modal_html',
                               files=kwargs['files']))
        self.response_commands.append(self.upload_file_command(0, **kwargs))
        return self.command_response()

    @staticmethod
    def upload_file_command(index, **kwargs):
        upload_file = {'options': {'progress': {'selector': f'#file_progress_bar_{index}'}},
                       'index': index,
                       'function': 'upload_file'}
        if 'upload_params' in kwargs:
            upload_file['upload_params'] = kwargs['upload_params']
        if 'drag_drop' in kwargs:
            upload_file['drag_drop'] = kwargs['drag_drop']
        else:
            upload_file['selector'] = kwargs['selector']
        return upload_file
