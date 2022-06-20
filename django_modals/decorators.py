from django.http import JsonResponse

from django_modals.helper import modal_button
from django_modals.messages import warning_modal


class ConfirmAjaxMethod:

    def __init__(self, *args, **kwargs):
        if args:
            raise Exception('Decorator class ConfirmAjaxMethod must be an instance and have ()')
        self.kwargs = kwargs

    @staticmethod
    def proc_message(message, **kwargs):
        return message

    @staticmethod
    def buttons(view, func, **kwargs):
        return [modal_button('Confirm', dict(function='post_modal',
                                             button=dict(ajax_method=func.__name__, confirm=True, **kwargs)),
                             'btn-warning'),
                modal_button('Cancel', 'close', 'btn-secondary')]

    def __call__(self, _func, **kwargs):
        def method(view, _ajax=True, **kwargs):
            if kwargs.get('confirm'):
                view.add_command('close')
                return _func(view, **kwargs)
            view.request.method = 'GET'

            message = self.proc_message(self.kwargs.get('message', 'Are you sure?'), **kwargs)
            title = self.kwargs.get('title', 'Warning')
            buttons = self.buttons(view, _func, **kwargs)
            return JsonResponse([{
                'function': 'modal_html',
                'html': warning_modal(message, view.request, title=title, buttons=buttons)
            }], safe=False)
        return method
