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
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.decorators import method_decorator

from crispy_forms.utils import render_crispy_form

from ajax_helpers.mixins import AjaxHelpers

from .forms import ModelCrispyForm
from .helper import render_modal, modal_button, modal_button_group, ajax_modal_redirect, modal_button_method, \
    ajax_modal_replace
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
    no_parent_template = 'django_modals/blank_page_form.html'

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'modal_mode'):
            self.modal_mode = True
        self.slug = {}

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
        context['modal_url'] = kwargs.get('modal_url', self.request.path)
        context['no_header_x'] = getattr(self, 'no_header_x', None)
        context['center_header'] = kwargs.get('center_header', getattr(self, 'center_header', None))
        context['size'] = kwargs.get('size', self.size)
        context['modal_type'] = self.kwargs.get('modal_type')
        return context

    def split_slug(self, kwargs):
        if 'slug' in kwargs:
            s = kwargs['slug'].split('-')
            if len(s) == 1:
                self.slug['pk'] = s[0]
            else:
                self.slug.update({s[k]: s[k+1] for k in range(0, int(len(s)-1), 2)})
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

    def button_refresh_modal(self, **_kwargs):
        return self.command_response(ajax_modal_replace(self.request, modal_class=self.__class__))

    def button_group(self):
        button_kwargs = {
            'button_group_class': self.kwargs.get('button_group_class', self.button_group_class),
            'button_container_class': self.kwargs.get('button_container_class', self.button_container_class)
        }
        button_kwargs = {k: v for k, v in button_kwargs.items() if v}
        return modal_button_group(self.buttons, **button_kwargs)

    def check_for_background_page(self, context):
        if not self.request.is_ajax() and self.modal_mode:
            context['modal_type'] = 'no-parent'
            context['no_header_x'] = True
            context['form'] = render_modal(template_name=self.template_name, **context)
            # noinspection PyAttributeOutsideInit
            self.template_name = self.no_parent_template

    def modal_replace(self, modal_name=None, modal_class=None, slug='-', **kwargs):
        return self.command_response(ajax_modal_replace(self.request, modal_name, slug=slug,
                                                        modal_class=modal_class, **kwargs))

    def message(self, message, title=None, **modal_kwargs):
        if title is not None:
            modal_kwargs['modal_title'] = title
        return self.modal_replace(modal_class=Modal, message=message, ajax_function='modal_html', **modal_kwargs)

    def confirm(self, message, title=None, button_group_type='confirm', **kwargs):
        return self.message(message, title=title, button_group_type=button_group_type, **kwargs)

    def modal_redirect(self, modal_name, slug='-'):
        return self.command_response(ajax_modal_redirect(modal_name, slug))


class BaseModal(BaseModalMixin, TemplateView):
    template_name = 'django_modals/modal_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_title'] = kwargs.get('modal_title', getattr(self, 'modal_title', None))
        self.check_for_background_page(context)
        return context


class Modal(BaseModal):

    def modal_content(self):
        return self.kwargs.get('message', '')

    def get_modal_buttons(self):
        button_group_type = self.kwargs.get('button_group_type')
        if button_group_type == 'confirm':
            return [
                modal_button_method('Confirm', self.kwargs.get('button_function', 'confirm'), 'btn-success'),
                modal_button('Cancel', 'close', 'btn-secondary')
            ]
        elif button_group_type == 'yes_cancel':
            return [
                modal_button_method('Yes', self.kwargs.get('button_function', 'confirm'), 'btn-danger'),
                modal_button('Cancel', 'close', 'btn-success')
            ]
        else:
            return [modal_button('OK', 'close', 'btn-success')]

    @property
    def extra_context(self):
        if not self._extra_content:
            modal_content = self.modal_content()
            if not self.buttons:
                self.buttons = self.get_modal_buttons()
            self._extra_content = {'form': mark_safe(modal_content + self.button_group())}
        return self._extra_content

    def __init__(self):
        if not hasattr(self, 'buttons'):
            self.buttons = []
        self._extra_content = None
        super().__init__()


class TemplateModal(Modal):

    modal_template = None

    @staticmethod
    def modal_context():
        return {}

    def modal_content(self):
        return render_to_string(self.modal_template, self.modal_context())


class FormModalMixin(BaseModalMixin):
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
        context = super().get_context_data(**kwargs)
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
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.field_attributes = {}
        self.triggers = {}

    def button_make_edit(self, **_kwargs):
        self.slug['modal'] = 'editdelete'
        new_slug = '-'.join([f'{k}-{v}' for k, v in self.slug.items()])
        self.request.method = 'GET'
        self.process = PROCESS_EDIT_DELETE
        self.request.path = reverse(self.request.resolver_match.url_name, kwargs={'slug': new_slug})
        return self.command_response('overwrite_modal',
                                     html=render_to_string(self.template_name, self.get_context_data()))

    def button_refresh_modal(self, **kwargs):
        if self.slug.get('readonly') or kwargs.get('whole_modal'):
            return super().button_refresh_modal()
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


class FormModal(FormModalMixin, TemplateResponseMixin, BaseFormView):
    pass


class ProcessFormFields:
    def __init__(self, form_fields, widgets=None, field_classes=None, labels=None, help_texts=None,
                 error_messages=None):
        self.fields = []
        self.widgets = widgets if widgets else {}
        self.labels = labels if labels else {}
        self.help_texts = help_texts if help_texts else {}
        self.error_messages = error_messages if error_messages else {}
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
                    if k == 'label':
                        self.labels[f[0]] = param_dict.pop(k)
                    if k == 'help_text':
                        self.help_texts[f[0]] = param_dict.pop(k)
                    if k == 'error_messages':
                        self.error_messages[f[0]] = param_dict.pop(k)
                    if k == 'layout_field_class':
                        self.layout_field_classes[f[0]] = param_dict.pop(k)
                if param_dict:
                    self.layout_field_params[f[0]] = param_dict
            else:
                self.fields.append(f)

    def form_init_kwargs(self):
        return {f: getattr(self, f) for f in ['layout_field_classes', 'layout_field_params'] if getattr(self, f, None)}

    def extra_kwargs(self):
        return {f: getattr(self, f) for f in ['widgets', 'field_classes', 'labels', 'help_texts',
                                              'error_messages'] if getattr(self, f, None)}


class ModelFormModal(SingleObjectMixin, FormModal):
    form_fields = []
    template_name = 'django_modals/modal_base.html'
    base_form = ModelCrispyForm
    delete_message = 'Are you sure you want to delete?'
    delete_title = 'Warning'
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
                                                      field_classes=getattr(self, 'field_classes', None),
                                                      labels=getattr(self, 'labels', None),
                                                      help_texts=getattr(self, 'help_texts', None),
                                                      error_messages=getattr(self, 'error_messages', None))

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
        return self.confirm(self.delete_message, self.delete_title, button_function='confirm_delete',
                            button_group_type='yes_cancel', size='md')

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


class MultiFormModal(BaseModal):
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
        # noinspection PyArgumentList
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
