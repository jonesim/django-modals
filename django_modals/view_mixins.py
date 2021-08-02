import json
import inspect
import collections
from django.forms.fields import Field
from django.forms.models import modelform_factory, fields_for_model
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateResponseMixin, TemplateView
from django.views.generic.edit import BaseFormView
from django.views.generic.detail import SingleObjectMixin
from django.template.loader import render_to_string
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator

from crispy_forms.utils import render_crispy_form

from ajax_helpers.mixins import AjaxHelpers

from .forms import ModelCrispyForm
from .helper import render_modal, modal_button, modal_button_group
from .processes import PROCESS_CREATE, PROCESS_VIEW, PROCESS_EDIT, PROCESS_DELETE, \
    PROCESS_EDIT_DELETE, PERMISSION_OFF, PERMISSION_DISABLE, user_has_perm, get_process, modal_url_type


class ModalException(Exception):
    pass


@method_decorator(ensure_csrf_cookie, name='dispatch')
class BaseModalMixin(AjaxHelpers):
    kwargs: dict
    button_group_class = None
    button_container_class = None
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}
    ajax_commands = ['button', 'select2']
    button_group_css = None
    size = 'lg'

    def __init__(self, modal_url=None):
        self.modal_url = modal_url
        super().__init__()
        self.slug = {'modalstyle': 'normal'}

    @staticmethod
    def permission(process=None):
        return True

    def get_context_data(self, **kwargs):
        if hasattr(super(), 'get_context_data'):
            # noinspection PyUnresolvedReferences
            context = super().get_context_data(**kwargs)
        else:
            context = {}
        context.update({'request': self.request, 'slug': self.slug})
        if self.modal_url is None:
            context['modal_url'] = self.request.path
        else:
            context['modal_url'] = self.modal_url
        if getattr(self, 'no_header_x', None):
            context['no_header_x'] = True
        context['size'] = self.size
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
        return True

    def dispatch(self, request, *args, **kwargs):
        self.split_slug(kwargs)
        if self.process_slug_kwargs():
            # noinspection PyUnresolvedReferences
            return super().dispatch(request, *args, **self.kwargs)
        else:
            raise ModalException('User does not have permission')

    def forward_modal(self, url_name):
        modal_url = reverse(url_name, kwargs={'slug': '-'})
        return resolve(modal_url).func.view_class.as_view()(self.request, modal_url=modal_url)

    def button_refresh_modal(self, **_kwargs):
        return self.command_response('')

    def button_group(self):
        kwargs = {a: getattr(self, a) for a in ['button_group_class', 'button_container_class'] if getattr(self, a)}
        return modal_button_group(self.buttons, **kwargs)

    def check_for_background_page(self, context):
        if not self.request.is_ajax():
            context['form'] = render_modal(template_name=self.template_name, modal_type='no-parent', **context)
            # noinspection PyAttributeOutsideInit
            self.template_name = 'django_modals/blank_page_form.html'

    def modal_replace(self, modal_name=None, modal_class=None, slug='-', **kwargs):
        self.request.method = 'get'
        if modal_class:
            view_class = modal_class
        else:
            self.request.path = reverse(modal_name, kwargs=dict(slug=slug))
            view_class = resolve(self.request.path).func.view_class
        return self.command_response({'function': 'overwrite_modal',
                                      'html': view_class.as_view()(self.request, slug=slug, **kwargs).rendered_content})

    def message(self, message, title=None):
        modal_kwargs = {'message': message}
        if title is not None:
            modal_kwargs['modal_title'] = title
        return self.modal_replace(modal_class=MessageModal, **modal_kwargs)

    def modal_redirect(self, modal_name, slug='-'):
        return self.command_response([{'function': 'close'},
                                      {'function': 'show_modal', 'modal': reverse(modal_name, kwargs={'slug': slug})}])

    def modal_render(self, contents=None, header_title=None, modal_buttons=None, **kwargs):
        return self.command_response('modal_html', html=render_modal(
            request=self.request, modal_buttons=modal_buttons, contents=contents, header_title=header_title, **kwargs
        ))


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
        elif 'modal_title' in kwargs:
            context['header_title'] = kwargs['modal_title']
        self.check_for_background_page(context)
        return context


class SimpleModal(BaseModal):

    def modal_content(self):
        return ''

    def modal_buttons(self):
        self.buttons = [modal_button('OK', 'close', 'btn-success')]

    @property
    def extra_context(self):
        if not self._extra_content:
            modal_content = self.modal_content()
            if not self.buttons:
                self.modal_buttons()
            self._extra_content = {'form': mark_safe(modal_content + self.button_group())}
        return self._extra_content

    def __init__(self):
        self.buttons = []
        self._extra_content = None
        super().__init__()


class MessageModal(SimpleModal):

    def modal_content(self):
        return self.kwargs.get('message', 'Are you sure?')

    def __init__(self):
        super().__init__()


class SimpleModalTemplate(SimpleModal):

    modal_template = None

    def modal_context(self):
        return {}

    def modal_content(self):
        return render_to_string(self.modal_template, self.modal_context())


class ModalFormMixin(BaseModalMixin):
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
        self.check_for_background_page(context)
        return context

    def add_trigger(self, field, trigger, conditions):
        self.field_attributes.setdefault(field, {})[trigger] = 'django_modal.alter_form(this, arguments[0])'
        self.triggers[field] = conditions

    def add_trigger_to_context(self, context):
        if not self.triggers:
            return
        modal_triggers = f'django_modal.modal_triggers.{context["form"].form_id}={json.dumps(self.triggers)}'
        reset_triggers = f'django_modal.reset_triggers(\'{context["form"].form_id}\')'
        context['script'] = mark_safe(context.get('script', '') + f';{modal_triggers};{reset_triggers};')

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'process'):
            self.process = None
        super().__init__(*args, **kwargs)
        self.field_attributes = {}
        self.triggers = {}

    def button_make_edit(self, **_kwargs):
        self.slug['modal'] = 'editdelete'
        new_slug = '-'.join([f'{k}-{v}' for k, v in self.slug.items() if k != 'modalstyle'])
        self.request.method = 'GET'
        self.process = PROCESS_EDIT_DELETE
        self.request.path = reverse(self.request.resolver_match.url_name, kwargs={'slug': new_slug})
        return self.command_response('overwrite_modal',
                                     html=render_to_string(self.template_name, self.get_context_data()))

    def button_refresh_modal(self, **kwargs):
        if self.slug.get('readonly'):
            return ''
        else:
            form = self.get_form()
            form.clear_errors()
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        kwargs['no_buttons'] = self.request.GET.get('no_buttons')
        if hasattr(self, 'form_setup') and callable(self.form_setup):
            kwargs['form_setup'] = self.form_setup
        kwargs.update({k: getattr(self, k, None) for k in ['modal_title', 'slug']})
        if hasattr(self, 'helper_class'):
            kwargs['helper_class'] = self.helper_class
        kwargs['process'] = self.process
        return kwargs


class BootstrapModalMixin(ModalFormMixin, TemplateResponseMixin, BaseFormView):
    pass


class ProcessFormFields:
    def __init__(self, form_fields, widgets=None, field_classes=None):
        self.fields = []
        self.widgets = widgets if widgets else {}
        self.field_classes = field_classes if field_classes else {}
        self.layout_field_classes = {}
        self.layout_field_params = {}

        for f in form_fields:
            if type(f) == tuple:
                self.fields.append(f[0])
                param_dict = dict(f[1])
                for k in f[1]:
                    if k == 'widget':
                        self.widgets[f[0]] = param_dict.pop(k)
                    if k == 'layout_field_class':
                        self.layout_field_classes[f[0]] = param_dict.pop(k)
                if param_dict:
                    self.layout_field_params[f[0]] = param_dict
            else:
                self.fields.append(f)

    def form_init_kwargs(self):
        return {f: getattr(self, f) for f in ['layout_field_classes', 'layout_field_params'] if getattr(self, f, None)}

    def extra_kwargs(self):
        return {f: getattr(self, f) for f in ['widgets', 'field_classes'] if getattr(self, f, None)}


class BootstrapModelModalMixin(SingleObjectMixin, BootstrapModalMixin):
    form_fields = []
    template_name = 'django_modals/modal_base.html'
    base_form = ModelCrispyForm
    delete_message = 'Are you sure you want to delete?'
    field_classes = None
    permission_delete = PERMISSION_DISABLE
    permission_edit = PERMISSION_OFF
    permission_view = PERMISSION_OFF
    permission_create = PERMISSION_OFF

    @staticmethod
    def formfield_callback(f, **kwargs):
        form_class = kwargs.get('form_class')
        if isinstance(form_class, Field):
            if hasattr(form_class, 'field_setup'):
                # noinspection PyCallingNonCallable
                form_class.field_setup(f)
            return form_class
        elif form_class:
            return form_class(**kwargs)
        return f.formfield(**kwargs)

    def __init__(self, *args, **kwargs):
        self.form_init_args = {}
        if not self.form_class:

            processed_form_fields = ProcessFormFields(self.form_fields, widgets=getattr(self, 'widgets', None),
                                                      field_classes=getattr(self, 'field_classes', None))

            self.form_init_args = processed_form_fields.form_init_kwargs()
            self.form_class = modelform_factory(self.model, form=self.base_form, fields=processed_form_fields.fields,
                                                formfield_callback=self.formfield_callback,
                                                **processed_form_fields.extra_kwargs())
        super().__init__(*args, **kwargs)
        self.object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update(self.form_init_args)
        return kwargs

    def button_confirm_delete(self, **_kwargs):
        if self.process in [PROCESS_DELETE, PROCESS_EDIT_DELETE]:
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

    def permission(self, process=None):
        if process is None:
            process = self.process
        perm_value = user_has_perm(self.__class__, self.request.user, process)
        if not perm_value and process == PROCESS_EDIT:
            self.process = PROCESS_VIEW
            perm_value = self.permission(PROCESS_VIEW)
        return perm_value

    def process_slug_kwargs(self):
        if 'pk' not in self.slug:
            self.process = PROCESS_CREATE
        elif 'modal' in self.slug:
            self.process = modal_url_type[self.slug['modal']]
        else:
            if self.process is None:
                self.process = PROCESS_EDIT_DELETE
        has_perm, self.process = get_process(self, self.request.user, self.process)

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
        return has_perm

    def select2_ajax_search(self, page_len=10, filter_field=None, filter_search='istartswith', search=None, page=None,
                            extra_filter=None, **_kwargs):
        field_name = inspect.stack()[1][3][len('select2_'):]
        field = fields_for_model(self.model, field_classes=self.field_classes, fields=[field_name],
                                 formfield_callback=self.formfield_callback)[field_name]
        if filter_field and search:
            query_filter = {f'{filter_field}__{filter_search}': search}
        else:
            query_filter = {}
        if extra_filter:
            query_filter.update(extra_filter)
        if hasattr(field, 'model'):
            # noinspection PyUnresolvedReferences
            choices = field.model.objects.filter(**query_filter)
        else:
            choices = field.choices.queryset.filter(**query_filter)
        if page:
            choices = choices[page_len * (page - 1): page_len * page + 1]
        if hasattr(field, 'select_str'):
            # noinspection PyCallingNonCallable
            results = [{'id': str(c.id), 'text': field.select_str(c)} for c in choices[:page_len]]
        else:
            results = [{'id': str(c.id), 'text': str(c)} for c in choices[:page_len]]
        return JsonResponse({'results': results, 'pagination': {'more': len(choices) > len(results)}})


MultiForm = collections.namedtuple('MultiForm', ['model', 'fields', 'id', 'initial', 'widgets'],
                                   defaults=[None, None, None, {}, []])


class MultiFormView(BaseModal):
    template_name = 'django_modals/multi_form.html'
    modal_title = ''
    base_form = ModelCrispyForm
    forms = []
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}

    def get_form_classes(self):
        for f in self.forms:
            processed_form_fields = ProcessFormFields(f.fields, widgets=f.widgets)
            self.form_setup_args.append({
                'form_class': modelform_factory(f.model, form=self.base_form, fields=processed_form_fields.fields,
                                                **processed_form_fields.extra_kwargs()),
                'processed_form_fields': processed_form_fields
            })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_setup_args = []

    @staticmethod
    def make_form_id(form, used_ids):
        form_id = form.model.__name__ + 'Form'
        if form_id not in used_ids:
            return form_id
        form_id += '_{}'
        count = 1
        while form_id.format(count) in used_ids:
            count += 1
        return form_id.format(count)

    def get_form_kwargs(self):
        all_kwargs = []
        used_ids = []
        if self.request.method in ('POST', 'PUT'):
            form_data = json.loads(self.request.body)
        else:
            form_data = {}
        for f in self.forms:
            form_id = f.id
            if not form_id:
                form_id = self.make_form_id(f, used_ids)
            used_ids.append(form_id)
            kwargs = f.initial.copy()
            kwargs['form_id'] = form_id
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
        self.get_form_classes()
        form_kwargs = self.get_form_kwargs()
        forms = []
        for c, s in enumerate(self.form_setup_args):
            kwargs = form_kwargs[c]
            kwargs.update(s['processed_form_fields'].form_init_kwargs())
            forms.append(s['form_class'](**kwargs))
        return forms

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
