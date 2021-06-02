import inspect
import importlib
from django.urls import reverse, resolve
from django.apps import apps
from django.views.generic import View


class ModalView(View):
    @staticmethod
    def find_from_module(modal_id, module_name):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__.startswith(module_name):
                if hasattr(obj, 'modal_name'):
                    if obj.modal_name == modal_id:
                        return obj

    @staticmethod
    def find_modal(modal_id):
        modal_id = modal_id.split('-')[0]
        for app in apps.get_app_configs():
            try:
                modal = ModalView.find_from_module(modal_id, app.name+'.modals')
                if modal is not None:
                    return modal
            except ModuleNotFoundError:
                pass

    def split_slug(self, kwargs):
        self.kwargs = kwargs
        s = kwargs['modal'].split('-')
        self.modal = s[0]
        if len(s) == 2:
            if s[1] == 'new':
                self.kwargs['new'] = True
            else:
                self.kwargs['pk'] = s[1]
        else:
            self.kwargs['initial'] = {}
            for k in range(1, int(len(s)-1), 2):
                self.kwargs['initial'][s[k]] = s[k+1]
            if 'pk' in self.kwargs['initial']:
                self.kwargs['pk'] = self.kwargs['initial']['pk']

    def get(self, request, *args, **kwargs):
        self.split_slug(kwargs)
        return ModalView.find_modal(self.modal).as_view()(request, *args, **self.kwargs)

    def post(self, request, *args, **kwargs):
        self.split_slug(kwargs)
        return ModalView.find_modal(self.modal).as_view()(request, *args, **self.kwargs)


class ModalName(View):

    def dispatch(self, request, *args, **kwargs):
        url = reverse(kwargs['name'], kwargs={'slug': kwargs['slug']})
        view_function, view_args, view_kwargs = resolve(url)
        return view_function(request, *view_args, **view_kwargs)
