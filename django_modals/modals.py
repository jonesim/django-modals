import base64
import binascii
import json
import inspect

from ajax_helpers.utils import is_ajax
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

from ajax_helpers.mixins import AjaxHelpers

from . import processes
from .forms import ModelCrispyForm
from .helper import render_modal, modal_button, modal_button_group, ajax_modal_redirect, modal_button_method, \
    ajax_modal_replace


class ModalException(Exception):
    pass


@method_decorator(ensure_csrf_cookie, name='dispatch')
class BaseModalMixin(AjaxHelpers):
    kwargs: dict
    button_group_class = None
    button_container_class = None
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}
    ajax_commands = ['button', 'select2', 'ajax']
    button_group_css = None
    size = 'lg'
    no_parent_template = 'django_modals/blank_page_form.html'

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'modal_mode'):
            self.modal_mode = True
        self.slug = {}

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
        context.update({'request': self.request, 'slug': self.slug})
        context['modal_url'] = kwargs.get('modal_url', self.request.get_full_path())
        context['no_header_x'] = getattr(self, 'no_header_x', None)
        context['center_header'] = kwargs.get('center_header', getattr(self, 'center_header', None))
        context['size'] = kwargs.get('size', self.size)
        context['modal_type'] = self.kwargs.get('modal_type')
        return context

    def split_slug(self, kwargs):
        if 'slug' in kwargs and kwargs['slug'] != '-':
            s = kwargs['slug'].split('-')
            if len(s) == 1:
                self.slug['pk'] = s[0]
            else:
                self.slug.update({s[k]: s[k+1] for k in range(0, int(len(s)-1), 2)})
            if 'pk' in self.slug:
                self.kwargs['pk'] = self.slug['pk']

    def process_slug_kwargs(self):
        return True

    def split_base64(self, kwargs):
        if 'base64' in kwargs:
            try:
                base64_data = json.loads(base64.urlsafe_b64decode(self.kwargs['base64']))
            except binascii.Error:
                raise ModalException('Error in modal base64 decode - This modal requires base64 not a slug')
            if not isinstance(base64_data, dict):
                base64_data = {'base64': base64_data}
            self.slug.update(base64_data)
            self.kwargs.update(base64_data)

    def dispatch(self, request, *args, **kwargs):
        self.split_slug(kwargs)
        self.split_base64(kwargs)
        if self.process_slug_kwargs():
            # noinspection PyUnresolvedReferences
            return super().dispatch(request, *args, **self.kwargs)
        else:
            raise ModalException('User does not have permission')

    def button_refresh_modal(self, **_kwargs):
        return self.command_response(ajax_modal_replace(self.request, modal_class=self.__class__,
                                                        slug=self.kwargs.get('slug', '-')))

    def button_group(self):
        button_kwargs = {
            'button_group_class': self.kwargs.get('button_group_class', self.button_group_class),
            'button_container_class': self.kwargs.get('button_container_class', self.button_container_class)
        }
        button_kwargs = {k: v for k, v in button_kwargs.items() if v}
        return modal_button_group(self.buttons, **button_kwargs)

    def check_for_background_page(self, context):
        if not is_ajax(self.request) and self.modal_mode:
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
        if 'buttons' in self.kwargs:
            return self.kwargs['buttons']
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

    def modal_context(self):
        context = self.kwargs.get('context', {})
        return context

    def modal_content(self):
        return render_to_string(self.modal_template, self.modal_context())

    def __init__(self, modal_template=None, modal_title=None, size=None, **kwargs):
        # These kwargs will be overwritten if called as_view()
        self.kwargs = kwargs
        if size:
            self.size = size
        if modal_title:
            self.modal_title = modal_title
        if modal_template:
            self.modal_template = modal_template
        super().__init__()

    def modal_html(self, request):
        self.request = request
        context = self.get_context_data()
        if 'message' in self.kwargs:
            context['message'] = self.kwargs['message']
        return render_to_string(self.template_name, context)


class FormModalMixin(BaseModalMixin):
    template_name = 'django_modals/modal_base.html'

    def form_invalid(self, form):
        if self.request.GET.get('formonly', False):
            form = self.get_form()
            return HttpResponse(str(form))
        return self.refresh_form(form)

    def post_save(self, created, form):
        pass

    def form_valid(self, form):
        org_id = self.object.pk if hasattr(self, 'object') else None
        save_function = getattr(form, 'save', None)
        if save_function:
            save_function()
        self.post_save(created=org_id is None, form=form)
        if not self.response_commands:
            self.add_command('reload')
        return self.command_response()

    def refresh_form(self, form):
        self.add_command('html', selector=f'#{form.helper.form_id}', parent=True, html=str(form))
        return self.command_response('modal_refresh_trigger', selector=f'#{form.helper.form_id}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['css'] = 'modal'
        if context['form']:
            context['header_title'] = context['form'].get_title()
        else:
            context['form'] = kwargs['message']
        context['focus'] = getattr(self, 'focus', True)
        self.check_for_background_page(context)
        return context

    def __init__(self, *args, **kwargs):
        if not hasattr(self, 'process'):
            self.process = None
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)

    def button_make_edit(self, **_kwargs):
        self.slug['modal'] = 'editdelete'
        new_slug = '-'.join([f'{k}-{v}' for k, v in self.slug.items()])
        self.request.method = 'GET'
        self.process = processes.PROCESS_EDIT_DELETE
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
        if hasattr(self, 'clean') and callable(self.clean):
            kwargs['clean'] = self.clean
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
    permission_delete = processes.PERMISSION_DISABLE
    permission_edit = processes.PERMISSION_OFF
    permission_view = processes.PERMISSION_OFF
    permission_create = processes.PERMISSION_OFF

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

    def get_form_class(self):
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
        return self.form_class

    def __init__(self, *args, **kwargs):
        self.form_init_args = {}
        super().__init__(*args, **kwargs)
        self.object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        if hasattr(self, 'form_id'):
            kwargs.update({'form_id': self.form_id})
        kwargs.update(self.form_init_args)
        return kwargs

    def object_delete(self):
        pass

    def button_confirm_delete(self, **kwargs):
        if self.process in [processes.PROCESS_DELETE, processes.PROCESS_EDIT_DELETE]:
            self.object.delete()
        self.object_delete()
        if not self.response_commands:
            if 'modal_querystring' in kwargs and 'on_delete=' in kwargs['modal_querystring']:
                self.add_command('redirect', url=base64.urlsafe_b64decode(kwargs['modal_querystring'][
                                                 kwargs['modal_querystring'].find('on_delete=') + 10:
                                                 ].split('&')[0]).decode('ascii'))
            else:
                self.add_command('close', no_refresh=True)
                self.add_command('reload')
        return self.command_response()

    def button_delete(self, **_kwargs):
        return self.confirm(self.delete_message, self.delete_title, button_function='confirm_delete',
                            button_group_type='yes_cancel', size='md')

    @staticmethod
    def user_has_perm(cls_or_instance, user, process):
        permission_type = getattr(cls_or_instance, processes.process_data[process].class_attribute)
        if permission_type == processes.PERMISSION_METHOD:
            # If permission method is not a staticmethod and function is called by class rather than instance
            # send None instead of self
            if inspect.isclass(cls_or_instance) and len(inspect.signature(cls_or_instance.permission).parameters) == 3:
                permission = cls_or_instance.permission(None, user, process)
            else:
                permission = cls_or_instance.permission(user, process)
        elif permission_type == processes.PERMISSION_OFF:
            permission = True
        elif permission_type == processes.PERMISSION_DISABLE:
            permission = False
        elif permission_type == processes.PERMISSION_AUTHENTICATED:
            permission = user.is_authenticated
        elif permission_type == processes.PERMISSION_STAFF:
            permission = user.is_staff or user.is_superuser
        else:
            # noinspection PyProtectedMember
            perms = [f'{cls_or_instance.model._meta.app_label}.{p}_{cls_or_instance.model._meta.model_name}'
                     for p in processes.process_data[process].django_permission]
            permission = user.has_perms(perms)
        return permission

    def get_process(self, user, process):
        while True:
            permission = self.user_has_perm(self, user, process)
            if permission:
                break
            process = processes.process_data[process].fallback
            if not process:
                break
        return permission, process

    def get_model(self):
        pass

    def get_queryset(self):
        query = super().get_queryset()
        if hasattr(self.model, 'query_filter'):
            return self.model.query_filter(query, self.request, modal=self)
        return query

    def process_slug_kwargs(self):
        if 'pk' not in self.slug:
            self.process = processes.PROCESS_CREATE
        elif 'modal' in self.slug:
            self.process = processes.modal_url_type[self.slug['modal']]
        else:
            if self.process is None:
                self.process = processes.PROCESS_EDIT_DELETE

        if self.model is None:
            if self.form_class:
                self.model = self.form_class.get_model(self.slug)
            else:
                self.model = self.get_model()
        if 'pk' in self.kwargs:
            self.object = self.get_object()
        else:
            self.initial = self.initial.copy()
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
        has_perm, self.process = self.get_process(self.request.user, self.process)
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


class MultiForm:

    def __init__(self, model, fields, form_id=None, initial=None, widgets=None, pk=None, field_classes=None,
                 labels=None, **kwargs):
        self.model = model
        self.fields = fields
        self.kwargs = kwargs
        self.form_id = form_id
        self.initial = initial if initial else {}
        self.widgets = widgets if widgets else {}
        self.field_classes = field_classes if field_classes else {}
        self.labels = labels if labels else {}
        self.pk = pk

    def make_form_id(self, used_ids):
        if not self.form_id:
            self.form_id = self.model.__name__ + 'Form'
            if self.form_id in used_ids:
                self.form_id += '_{}'
                count = 1
                while self.form_id.format(count) in used_ids:
                    count += 1
                self.form_id = self.form_id.format(count)
        used_ids.append(self.form_id)

    def get_kwargs(self):
        kwargs = {'form_id': self.form_id, 'initial': self.initial, 'no_buttons': True}
        if self.pk:
            kwargs.update({'instance': self.model.objects.get(pk=self.pk)})
        kwargs.update(self.kwargs)
        return kwargs


class DictGetList(dict):
    """
    Adds getlist to dict to make dict work more like Django's MultiValueDict
    """
    def getlist(self, key, default=None):
        try:
            values = super().__getitem__(key)
        except KeyError:
            if default is None:
                return []
            return default
        else:
            return values if isinstance(values, list) else [values]


class MultiFormModal(BaseModal):
    template_name = 'django_modals/multi_form.html'
    modal_title = ''
    base_form = ModelCrispyForm
    forms = []
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}

    def get_form_classes(self):
        for f in self.forms:
            processed_form_fields = ProcessFormFields(f.fields, widgets=f.widgets, field_classes=f.field_classes,
                                                      labels=f.labels)
            self.form_setup_args.append({
                'form_class': modelform_factory(f.model, form=self.base_form, fields=processed_form_fields.fields,
                                                **processed_form_fields.extra_kwargs()),
                'processed_form_fields': processed_form_fields
            })

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.form_setup_args = []

    def get_form_kwargs(self):
        all_kwargs = []
        used_ids = []
        if self.request.method in ('POST', 'PUT'):
            form_data = json.loads(self.request.body)
            for f in form_data:
                if isinstance(form_data[f], dict):
                    form_data[f] = DictGetList(**form_data[f])
        else:
            form_data = {}
        for f in self.forms:
            f.make_form_id(used_ids)
            kwargs = f.get_kwargs()
            if self.request.method in ('POST', 'PUT'):
                kwargs.update({
                    'data': form_data[f.form_id],
                    # 'files': self.request.FILES,
                })
            if hasattr(f, 'clean') and callable(f.clean):
                kwargs['clean'] = f.clean
            elif hasattr(self, 'clean') and callable(self.clean):
                kwargs['clean'] = self.clean
            if hasattr(self, 'get_instances') and callable(self.get_instances):
                kwargs['instance'] = self.get_instances(f.form_id)
            if hasattr(f, 'form_setup') and callable(f.form_setup):
                kwargs['form_setup'] = f.form_setup
            elif hasattr(self, 'form_setup') and callable(self.form_setup):
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
            form = s['form_class'](**kwargs)
            for field_name, field in form.fields.items():
                field.widget.attrs.update({'id': f'id_{c}_{field_name}'})
            forms.append(form)
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
                         html=' '.join([str(f) for f in forms]))
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
