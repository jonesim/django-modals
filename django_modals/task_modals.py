import inspect

from ajax_helpers.utils import ajax_command

from django_modals.helper import progress_bar
from django_modals.modals import Modal


class TaskModal(Modal):

    task = None
    refresh_ms = 200
    config = {}

    def __init__(self, task=None):
        if task:
            self.task = task
        super().__init__()

    def modal_content(self):
        self.buttons = ['']
        self.size = self.config.get('size', 'md')
        return '<div id="task_message">{}</div>{}'.format(self.config.get('message', 'Please wait'),
                                                          progress_bar() if self.config.get('progress') else '')

    def state_success(self, task_result):
        return self.command_response(task_result.result['commands'])

    def state_failure(self, task_result):
        return self.command_response([ajax_command('close'),
                                     ajax_command('message', text='Task Failed. \n' + str(task_result.result))])

    def state_revoked(self, _task_result):
        return self.command_response([ajax_command('close'), ajax_command('message', text='Task Revoked')])

    def ajax_check_result(self, *, task_id, **_kwargs):
        task_result = self.task.AsyncResult(task_id)

        if hasattr(self, 'state_' + task_result.state.lower()):
            return getattr(self, 'state_' + task_result.state.lower())(task_result)

        if task_result.info:
            self.add_command('set_css', selector='#file_progress_bar', prop='width',
                             val=f'{task_result.info.get("current", 0)}%')
            if 'message' in task_result.info:
                self.add_command('html', selector='#task_message', html=task_result.info['message'])

        return self.command_response(
            'timeout', time=self.refresh_ms,
            commands=[
                ajax_command('ajax_post', url=self.request.path,
                             data={'ajax': 'check_result', 'task_id': task_result.id})]
        )

    def ajax_start_task(self, **_kwargs):
        task = self.task.delay(slug=self.slug, user_id=self.request.user.id)
        return self.ajax_check_result(task_id=task.id)

    def get_context_data(self, **kwargs):
        self.add_page_command('ajax_post', url=self.request.path, data={'ajax': 'start_task'})
        if 'config' in inspect.signature(self.task.run).parameters:
            self.config = self.task(config=True)
        self.modal_title = self.config.get('title', 'Processing')
        context = super().get_context_data(**kwargs)
        return context
