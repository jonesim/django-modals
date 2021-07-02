import json
import collections
from django.core.handlers.wsgi import WSGIRequest
from crispy_forms.utils import render_crispy_form
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.edit import BaseFormView
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
from ajax_helpers.mixins import AjaxHelpers
from .forms import ModelCrispyForm
from .helper import render_modal
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

'''
modalstyle

form - (AJAX) just send form html 
window - just send window but no form data which is loaded later
normal - page including form data
windowform - formpart of window
POST - just return form data
'''


@method_decorator(ensure_csrf_cookie, name='dispatch')
class BaseModalMixin(AjaxHelpers):
    request: WSGIRequest
    kwargs: dict
    ajax_commands = ['button', 'select2']

    def __init__(self, modal_url=None):
        self.modal_url = modal_url
        super().__init__()
        self.slug = {'modalstyle': 'normal'}

    def get_context_data(self, **kwargs):
        if hasattr(super(), 'get_context_data'):
            # noinspection PyUnresolvedReferences
            context = super().get_context_data(**kwargs)
        else:
            context = {}
        context.update({'request': self.request, 'slug': self.slug})
        if self.slug['modalstyle'] == 'windowform':
            context['css'] = 'window'
        else:
            context['css'] = 'modal'
        if self.modal_url is None:
            context['modal_url'] = self.request.path
        else:
            context['modal_url'] = self.modal_url
        if getattr(self, 'no_header_x', None):
            context['no_header_x'] = True
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.content_type == 'multipart/form-data':
            response = request.POST
            for t in self.ajax_commands:
                if t in response and hasattr(self, f'{t}_{response[t]}'):
                    return getattr(self, f'{t}_{response[t]}')(**response)
        if hasattr(super(), 'post'):
            return super().post(request, *args, **kwargs)

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
        self.split_slug(kwargs)
        self.process_slug_kwargs()
        # noinspection PyUnresolvedReferences
        return super().dispatch(request, *args, **self.kwargs)

    def forward_modal(self, url_name):
        modal_url = reverse(url_name, kwargs={'slug': '-'})
        return resolve(modal_url).func.view_class.as_view()(self.request, modal_url=modal_url)

    def button_refresh_modal(self, **_kwargs):
        return self.command_response('')

    @staticmethod
    def button(title, commands, css_class):
        if type(commands) == str:
            params = [{'function': commands}]
        elif type(commands) == dict:
            params = [commands]
        else:
            params = commands
        return f'''<button onclick='django_modal.process_commands_lock({json.dumps(params)})' 
                class="btn {css_class}">{title}</button>'''

    def button_group(self, button_str=None):
        if button_str is not None:
            return f'<div class="form-buttons"><div class="btn-group">{button_str}</div></div>'
        if hasattr(self, 'buttons') and self.buttons:
            return f'<div class="form-buttons"><div class="btn-group">{"".join(self.buttons)}</div></div>'
        return ''


class BaseModal(BaseModalMixin, TemplateView):
    template_name = 'django_modals/modal_base.html'

    def get_context_data(self, **kwargs):
        get_context_data = getattr(super(), 'get_context_data', None)
        if get_context_data:
            context = get_context_data(**kwargs)
        else:
            context = {}
        if hasattr(self, 'modal_title'):
            context['header_title'] = self.modal_title
        if not self.request.is_ajax():
            context['form'] = render_modal(template_name=self.template_name, **context)
            self.template_name = 'django_modals/blank_page_form.html'
        return context


class SimpleModal(BaseModal):

    def modal_content(self):
        return ''

    @property
    def extra_context(self):
        if not self._extra_content:
            self._extra_content = {'form': mark_safe(self.modal_content() + self.button_group())}
        return self._extra_content

    def __init__(self):
        self.buttons = []
        self._extra_content = None
        super().__init__()


class ModalFormMixin(BaseModalMixin):
    request: WSGIRequest
    template_name = 'django_modals/modal_base.html'

    def form_invalid(self, form):
        if self.request.GET.get('formonly', False):
            form = self.get_form()
            return HttpResponse(render_crispy_form(form))
        return self.refresh_form(form)

    def form_valid(self, form):
        save_function = getattr(form, 'save', None)
        if save_function:
            save_function()
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    def refresh_form(self, form):
        self.add_command('html', selector=f'#{form.helper.form_id}', parent=True, html=render_crispy_form(form))
        return self.command_response('modal_refresh_trigger', selector=f'#{form.helper.form_id}')

    def get_context_data(self, **kwargs):
        get_context_data = getattr(super(), 'get_context_data', None)
        if get_context_data:
            context = get_context_data(**kwargs)
        else:
            context = {}
        context['css'] = 'modal'
        if context['form']:
            context['header_title'] = context['form'].get_title()
        else:
            context['form'] = kwargs['message']
        for f in self.field_attributes:
            context['form'].helper[f].update_attributes(**self.field_attributes[f])
        self.add_trigger_to_context(context)
        if not self.request.is_ajax():
            context['form'] = render_modal(template_name=self.template_name, **context)
            self.template_name = 'django_modals/blank_page_form.html'
        return context

    def add_trigger(self, field, trigger, conditions):
        self.field_attributes.setdefault(field, {})[trigger] = 'django_modal.alter_form(this)'
        self.triggers[field] = conditions

    def add_trigger_to_context(self, context):
        if not self.triggers:
            return
        modal_triggers = f'django_modal.modal_triggers.{context["form"].form_id}={json.dumps(self.triggers)}'
        reset_triggers = f'django_modal.reset_triggers(\'{context["form"].form_id}\')'
        context['script'] = mark_safe(context.get('script', '') + f';{modal_triggers};{reset_triggers};')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_attributes = {}
        self.triggers = {}

    def button_refresh_modal(self, **_kwargs):
        form = self.get_form()
        form.clear_errors()
        return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        kwargs['no_buttons'] = self.request.GET.get('no_buttons')
        if hasattr(self, 'form_setup') and callable(self.form_setup):
            kwargs['form_setup'] = self.form_setup
        kwargs.update({k: getattr(self, k, None) for k in ['modal_title', 'form_delete', 'slug']})
        return kwargs


class BootstrapModalMixin(ModalFormMixin, TemplateResponseMixin, BaseFormView):
    pass


class BootstrapModelModalMixin(SingleObjectMixin, BootstrapModalMixin):
    form_fields = []
    template_name = 'django_modals/modal_base.html'
    base_form = ModelCrispyForm
    delete_message = 'Are you sure you want to delete?'

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
        if form.form_delete:
            self.object.delete()
        if not self.response_commands:
            self.add_command('close', no_refresh=True)
            self.add_command('reload')
        return self.command_response()

    def button_delete(self, **_kwargs):
        return self.command_response(
            'modal_html', html=render_modal(template_name='django_modals/confirm.html', modal_url=self.request.path,
                                            size='md', button_function='confirm_delete', message=self.delete_message)
        )

    def process_slug_kwargs(self):
        if self.model is None:
            self.model = self.form_class.get_model(self.slug)
        if 'pk' in self.kwargs:
            self.object = self.get_object()
        else:
            self.object = self.model()
            # noinspection PyProtectedMember
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


class MultiFormView(BaseModal):
    template_name = 'django_modals/multi_form.html'
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
            if hasattr(self, 'form_setup') and callable(self.form_setup):
                kwargs['form_setup'] = self.form_setup
            all_kwargs.append(kwargs)
        all_kwargs[-1]['no_buttons'] = False
        return all_kwargs

    def get_forms(self):
        form_kwargs = self.get_form_kwargs()
        return [form_class(**form_kwargs[c]) for c, form_class in enumerate(self.get_form_classes())]

    def get_context_data(self, **kwargs):
        self.extra_context = {
            'forms': self.get_forms(),
            'header_title': self.modal_title
        }
        context = super().get_context_data(**kwargs)
        return context

    def refresh_form(self, forms):
        self.add_command('html', selector=f'#{forms[0].form_id}', parent=True,
                         html=' '.join([render_crispy_form(f) for f in forms]))
        return self.command_response('modal_refresh_trigger', selector=f'#{forms[0].form_id}')

    def forms_valid(self, forms):
        pass

    def post(self, request, *args, **kwargs):
        post_response = super().post(request, *args, **kwargs)
        if post_response:
            return post_response
        forms = self.get_forms()
        for f in forms:
            if not f.is_valid():
                return self.refresh_form(forms)
        return self.forms_valid({f.helper.form_id: f for f in forms})
