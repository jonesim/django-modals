import os

from django.http import HttpResponse
from django.views import View

from modal_examples.tasks import DemoTask
from .views import MainMenuTemplateView


class TaskViews(MainMenuTemplateView):

    template_name = 'example_views/celery_tasks.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('demo_task_modal,attachment-True', 'Download attachment'),
            ('demo_task_modal,attachment-False', 'View Download'),

        )


class GetTaskFile(View):

    def get(self, request, task_id):
        task_result = DemoTask.AsyncResult(task_id)
        file = open(task_result.result['download'], 'rb')
        response = HttpResponse(content_type=task_result.result['type'])
        response['Content-Disposition'] = (f'{"attachment" if task_result.result.get("attachment") else "inline"};'
                                           f' filename={task_result.result["filename"]}')
        response.write(file.read())
        file.close()
        os.remove(task_result.result['download'])
        return response
