import json
import collections
from crispy_forms.utils import render_crispy_form
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.edit import FormMixin, ProcessFormView
from django.views.generic.detail import SingleObjectMixin
from django.template.loader import render_to_string
from django.shortcuts import render
from django.core.handlers.wsgi import WSGIRequest
from ajax_helpers.mixins import AjaxHelpers
from .forms import ModelCrispyForm

'''
modalstyle

form - (AJAX) just send form html 
window - just send window but no form data which is loaded later
normal - page including form data
windowform - formpart of window
POST - just return form data
'''


class BaseModalMixin:

    def __init__(self):
        super().__init__()
        self.slug = {'modalstyle': 'normal'}

    def get_context_data(self, **kwargs):
        if hasattr(super(), 'get_context_data'):
            context = super().get_context_data(**kwargs)
        else:
            context = {}
        context.update({'request': self.request, 'slug': self.slug})
        if self.slug['modalstyle'] == 'windowform':
            context['css'] = 'window'
        else:
            context['css'] = 'modal'
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.content_type == 'multipart/form-data':
            response = request.POST
            for t in self.ajax_commands:
                if t in response and hasattr(self, f'{t}_{response[t]}'):
                    return getattr(self, f'{t}_{response[t]}')(**response)
        if hasattr(super(), 'post'):
            return super().post(request, *args, **kwargs)


class BaseModal(BaseModalMixin, AjaxHelpers, TemplateView):
    pass


class BootstrapModalMixinBase(BaseModalMixin, AjaxHelpers, TemplateResponseMixin, ProcessFormView):
    kwargs: dict
    request: WSGIRequest
    ajax_commands = ['button', 'select2']

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
        return super().dispatch(request, *args, **self.kwargs)

    def get(self, request, *args, **kwargs):
        if self.slug['modalstyle'] == 'window':
            return render(request, 'modal/blank_form.html', context={'request': request})

        if self.slug['modalstyle'] == 'form':
            return super().get(request, *args, **kwargs)

        modal_html = render_to_string(self.template_name, self.get_context_data(**kwargs))
        return render(request, 'modal/blank_form.html', context={'modal_form': modal_html, 'request': request})

    def refresh_form(self, form):
        self.add_command('html', selector=f'#{form.Meta.form_id}', parent=True, html=render_crispy_form(form))
        return self.command_response('modal_refresh_trigger', selector=f'#{form.Meta.form_id}')


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
        return self.refresh_form(form)

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

    def button_refresh_form(self, **_kwargs):
        form = self.get_form()
        form.clear_errors()
        return self.form_invalid(form)


class BootstrapModelModalMixin(SingleObjectMixin, BootstrapModalMixin):
    form_fields = []
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

    def button_confirm_delete(self, **_kwargs):
        form = self.get_form()
        if form.Meta.delete:
            self.object.delete()
        if not self.response_commands:
            self.add_command('close', no_refresh=True)
            self.add_command('reload')
        return self.command_response()

    def button_delete(self, **_kwargs):
        return self.command_response(
            'modal_html', html=render_to_string('modal/confirm.html', {
                'request': self.request, 'css': 'modal', 'size': 'md',
                'button_function': 'confirm_delete',
                'message': 'Are you sure you want to delete?'
            })
        )

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


MultiForm = collections.namedtuple('MultiForm', ['model', 'fields', 'id', 'initial', 'widgets'],
                                   defaults=[None, None, None, {}, []])


class MultiFormView(BootstrapModalMixinBase):
    template_name = 'modal/multi_form.html'
    modal_title = ''
    base_form = ModelCrispyForm
    forms = []

    def get_form_classes(self):
        return [modelform_factory(f.model, form=self.base_form, fields=f.fields, widgets=f.widgets)
                for f in self.forms]

    def get_form_kwargs(self):
        all_kwargs = []
        if self.request.method in ('POST', 'PUT'):
            form_data = json.loads(self.request.body)
        else:
            form_data = {}
        for f in self.forms:
            form_id = f.id
            if not form_id:
                form_id = f.model.__name__ + 'Form'
            kwargs = f.initial.copy()
            kwargs['no_buttons'] = True
            if self.request.method in ('POST', 'PUT'):
                kwargs.update({
                    'data': form_data[form_id],
                    # 'files': self.request.FILES,
                })
            all_kwargs.append(kwargs)
        all_kwargs[-1]['no_buttons'] = False
        return all_kwargs

    def get_forms(self):
        form_kwargs = self.get_form_kwargs()
        return [form_class(**form_kwargs[c]) for c, form_class in enumerate(self.get_form_classes())]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['forms'] = self.get_forms()
        context['modal_title'] = self.modal_title
        return context

    def refresh_form(self, forms):
        self.add_command('html', selector=f'#{forms[0].Meta.form_id}', parent=True,
                         html=' '.join([render_crispy_form(f) for f in forms]))
        return self.command_response('modal_refresh_trigger', selector=f'#{forms[0].Meta.form_id}')

    def forms_valid(self):
        pass

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        for f in forms:
            if not f.is_valid():
                return self.refresh_form(forms)
        return self.forms_valid({f.helper.form_id: f for f in forms})
