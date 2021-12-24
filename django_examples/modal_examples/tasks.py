from time import sleep

from celery import shared_task
from tempfile import NamedTemporaryFile
from ajax_helpers.utils import ajax_command
from django.urls import reverse


@shared_task(bind=True)
def DemoTask(self, config=False, **kwargs):
    message = 'initial'
    if config:
        return {'progress': True, 'message': message, 'title': 'Processing....'}

    for i in range(100):
        if i > 66:
            message = 'last part'
        elif i > 33:
            message = 'middle third'
        self.update_state(state='PROGRESS', meta={'current': i, 'total': 100, 'message': message, 'kwargs': kwargs})
        sleep(0.01)
    f = NamedTemporaryFile(delete=False)
    pdf = open('/app/sample.pdf', 'rb')
    f.write(pdf.read())
    f.close()
    return {
            'download': f.name,
            'commands': [ajax_command('message', text='Completed Task'),
                         ajax_command('close'),
                         ajax_command('redirect', url=reverse('get_task_file', args=(self.request.id, )))],
            'type': 'application/pdf',
            'filename': 'test1.pdf',
            'attachment': kwargs['slug'].get('attachment') == 'True'}
