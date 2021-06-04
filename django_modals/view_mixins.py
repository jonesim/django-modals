import json
from crispy_forms.utils import render_crispy_form
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView
from django.views.generic.detail import SingleObjectMixin
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from .forms import ModelCrispyForm

'''
modalstyle

form - (AJAX) just send form html 
window - just send window but no form data which is loaded later
normal - page including form data
windowform - formpart of window
POST - just return form data
'''


class BootstrapModalMixinBase(ProcessFormView, TemplateResponseMixin):
    kwargs: dict
    request: WSGIRequest

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
        context = {'request': self.request, 'slug': self.slug}
        if self.slug['modalstyle'] == 'windowform':
            context['css'] = 'window'
        else:
            context['css'] = 'modal'
        return context

    def get(self, request, *args, **kwargs):
        if self.slug['modalstyle'] == 'window':
            return render(request, 'modal/blank_form.html', context={'request': request})

        if self.slug['modalstyle'] == 'form':
            return super().get(request, *args, **kwargs)

        modal_html = render_to_string(self.template_name, self.get_context_data(**kwargs))
        return render(request, 'modal/blank_form.html', context={'modal_form': modal_html, 'request': request})


class BootstrapModalMixin(BootstrapModalMixinBase, FormMixin):

    template_name = 'modal/modal_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(FormMixin.get_context_data(self, **kwargs))
        return context

    def form_invalid(self, form):
        if self.request.GET.get('formonly', False):
            form = self.get_form()
            return HttpResponse(render_crispy_form(form))
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        modal_config = {'slug': self.slug,
                        'user': self.request.user}

        if self.request.GET.get('no_buttons'):
            kwargs['no_buttons'] = True
        if hasattr(self, 'modal_title'):
            modal_config['modal_title'] = self.modal_title
        if hasattr(self, 'form_delete'):
            modal_config['form_delete'] = self.form_delete
        if hasattr(self, 'form_setup'):
            modal_config['form_setup'] = self.form_setup
        kwargs['modal_config'] = modal_config
        return kwargs

    def button_refresh_form(self, _request, *_args, **kwargs):
        form = self.get_form()
        form.clear_errors()
        kwargs['form'] = form
        return self.render_to_response(self.get_context_data(**kwargs))


class BootstrapModelModalMixin(SingleObjectMixin, BootstrapModalMixin):
    form_fields: list
    template_name = 'modal/modal_form.html'
    base_form = ModelCrispyForm

    def __init__(self, *args, **kwargs):
        if not self.form_class:
            extra_kwargs = {}
            if hasattr(self, 'widgets'):
                extra_kwargs['widgets'] = self.widgets
            self.form_class = modelform_factory(self.model, form=self.base_form, fields=self.form_fields,
                                                **extra_kwargs)
        super().__init__(*args, **kwargs)
        self.object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs

    def button_confirm_delete(self, _request, *_args, **_kwargs):
        form = self.get_form()
        if form.Meta.delete:
            self.object.delete()
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    @staticmethod
    def button_delete(request, *_args, **_kwargs):
        return render(request, 'modal/confirm.html',
                      {'request': request, 'css': 'modal', 'size': 'md', 'message': 'Are you sure you want to delete?'})

    def process_slug_kwargs(self):
        if self.model is None:
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
