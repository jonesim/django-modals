import base64
import inspect

from django.forms.fields import Field
from django.forms.models import modelform_factory, fields_for_model
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import BaseFormView

from django_modals import processes
from django_modals.forms import ModelCrispyForm, ProcessFormFields
from django_modals.modals.modals import BaseModalMixin


class FormModalMixin(BaseModalMixin):
    request: HttpRequest

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
        kwargs['page_commands'] = self.page_commands
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
