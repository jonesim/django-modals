import json
from functools import cached_property

from django.forms.models import modelform_factory

from django_modals.forms import ModelCrispyForm, ProcessFormFields
from django_modals.modals import BaseModal


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


class MultiForm:

    def __init__(self, model, fields, form_id=None, initial=None, widgets=None, pk=None, field_classes=None,
                 labels=None, form_class=None, help_texts=None, **kwargs):
        self.model = model
        self.fields = fields
        self.kwargs = kwargs
        self.form_id = form_id
        self.initial = initial if initial else {}
        self.widgets = widgets if widgets else {}
        self.field_classes = field_classes if field_classes else {}
        self.help_texts = help_texts if help_texts else {}
        self.labels = labels if labels else {}
        self.pk = pk
        self.form_class = form_class if form_class else ModelCrispyForm

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


class MultiFormModal(BaseModal):
    template_name = 'django_modals/multi_form.html'
    modal_title = ''
    forms = []
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}

    def get_form_classes(self):
        for f in self.forms:
            processed_form_fields = ProcessFormFields(f.fields, widgets=f.widgets, field_classes=f.field_classes,
                                                      help_texts=f.help_texts, labels=f.labels)
            self.form_setup_args.append({
                'form_class': modelform_factory(f.model, form=f.form_class, fields=processed_form_fields.fields,
                                                **processed_form_fields.extra_kwargs()),
                'processed_form_fields': processed_form_fields
            })

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super().__init__(*args, **kwargs)
        self.form_setup_args = []

    @cached_property
    def form_data(self):
        if self.request.method in ('POST', 'PUT'):
            form_data = json.loads(self.request.body)
            for f in form_data:
                if isinstance(form_data[f], dict):
                    form_data[f] = DictGetList(**form_data[f])
        else:
            form_data = {}
        return form_data

    def get_form_kwargs(self):
        all_kwargs = []
        used_ids = []
        first = True
        for f in self.forms:
            f.make_form_id(used_ids)
            kwargs = f.get_kwargs()
            if first:
                kwargs['page_commands'] = self.page_commands
            if f.form_id in self.form_data:
                kwargs.update({
                    'data': self.form_data[f.form_id],
                    # 'files': self.request.FILES,
                })
            if hasattr(f, 'clean') and callable(f.clean):
                kwargs['clean'] = f.clean
            elif hasattr(self, 'clean') and callable(self.clean):
                kwargs['clean'] = self.clean
            if hasattr(self, 'get_instances') and callable(self.get_instances):
                kwargs['instance'] = self.get_instances(f.form_id)
            if hasattr(self, f'{f.form_id}_get_initial'):
                kwargs['initial'] = getattr(self, f'{f.form_id}_get_initial')()
            if hasattr(f, 'form_setup') and callable(f.form_setup):
                kwargs['form_setup'] = f.form_setup
            elif hasattr(self, 'form_setup') and callable(self.form_setup):
                kwargs['form_setup'] = self.form_setup
            all_kwargs.append(kwargs)
            first = False
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
        context['focus'] = getattr(self, 'focus', True)
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

    def resend_forms(self):
        all_forms = self.get_forms()
        for f in all_forms:
            f.clear_errors()
        return self.refresh_form(all_forms)
