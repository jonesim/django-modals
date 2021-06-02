import json
from crispy_forms.utils import render_crispy_form
from django.http import HttpResponse
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectTemplateResponseMixin
from django.views.generic.edit import ProcessFormView, ModelFormMixin
from django.template.loader import render_to_string
from django.shortcuts import render


'''
modalstyle

form - (AJAX) just send form html 
window - just send window but no form data which is loaded later
normal - page including form data
windowform - formpart of window
POST - just return form data
'''


class BootstrapModalMixinBase(object):

    def __init__(self):
        super().__init__()
        self.slug = {'modalstyle': 'normal'}
        self.response_commands = []

    def split_slug(self, kwargs):
        if 'slug' not in kwargs:
            return
        s = kwargs['slug'].split('-')
        if len(s) == 1:
            if s[0] != 'new':
                self.slug['pk'] = s[0]
        else:
            for k in range(0, int(len(s)-1), 2):
                self.slug[s[k]] = s[k+1]
        if 'pk' in self.slug:
            self.kwargs['pk'] = self.slug['pk']

    def process_slug_kwargs(self):
        pass

    def post(self, request, *args, **kwargs):
        return super().post(self, request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.slug['modalstyle'] = 'form'
        self.split_slug(kwargs)
        self.process_slug_kwargs()

        if request.method.lower() == 'post':
            ajax_functions = ['button_name', 'select2_name']
            for f in ajax_functions:
                if f in request.POST:
                    function_name = f[:-4] + request.POST[f].lower()
                    if hasattr(self, function_name):
                        return getattr(self, function_name)(request, *args, **self.kwargs)

        return super().dispatch(request, *args, **self.kwargs)

    def button_refresh_form(self, request, *args, **kwargs):
        form = self.get_form()
        form.clear_errors()
        kwargs['form'] = form
        return self.render_to_response(self.get_context_data(**kwargs))

    def add_command(self, function_name, params=None):
        if params is None:
            params = {}
        params['function'] = function_name
        self.response_commands.append(params)

    def command_response(self, function_name=None, params=None):
        if function_name is not None:
            self.add_command(function_name, params)
        return HttpResponse(json.dumps(self.response_commands), content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.slug['modalstyle'] == 'windowform':
            context['css'] = 'window'
        else:
            context['css'] = 'modal'
        context['request'] = self.request
        context['slug'] = self.slug
        return context

    def form_valid(self, form):
        form.save()
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    def form_invalid(self, form):
        if self.request.GET.get('formonly', False):
            form = self.get_form()
            return HttpResponse(render_crispy_form(form))
        return super().form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['modal_config'] = {'slug': self.slug,
                                  'user': self.request.user}
        if self.request.GET.get('no_buttons'):
            kwargs['no_buttons'] = True
        return kwargs

    def get(self, request, *args, **kwargs):
        if self.slug['modalstyle'] == 'window':
            return render(request, 'blank_form.html', context={'request': request})

        if self.slug['modalstyle'] == 'form':
            return super().get(request, *args, **kwargs)

        modal_html = render_to_string(self.template_name, self.get_context_data(**kwargs))
        return render(request, 'blank_form.html', context={'modal_form': modal_html, 'request': request})


class BootstrapModalMixin(BootstrapModalMixinBase, FormView):

    template_name = 'modal_base.html'


class BootstrapModelModalMixin(BootstrapModalMixinBase, SingleObjectTemplateResponseMixin, ModelFormMixin,
                               ProcessFormView):

    template_name = 'modal_base.html'

    def button_confirm_delete(self, request, *args, **kwargs):
        self.model = self.form_class.get_model(self.slug)
        self.object = self.get_object()
        if hasattr(self.object, 'can_delete') and not self.object.can_delete():
            return render(request, 'modal/ok.html', {'css': 'modal', 'size': 'md',
                                                     'message': self.object.delete_error_message})
        self.object.delete()
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    @staticmethod
    def button_delete(request, *args, **kwargs):
        return render(request, 'modal/confirm.html',
                      {'request': request, 'css': 'modal', 'size': 'md', 'message': 'Are you sure you want to delete?'})

    def process_slug_kwargs(self):
        self.model = self.form_class.get_model(self.slug)
        if 'pk' in self.kwargs:
            self.object = self.get_object()
        else:
            self.object = self.model()
            fields = self.model._meta.get_fields()
            field_dict = {}
            for f in fields:
                field_dict[f.name.lower()] = f
            for i in self.slug:
                if i in field_dict and field_dict[i].many_to_many:
                    self.initial[i] = [self.slug[i]]
                else:
                    setattr(self.object, i, self.slug[i])
