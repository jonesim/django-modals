import json
from django import forms
from django.apps import apps
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Div
from crispy_forms.bootstrap import StrictButton
from crispy_forms.utils import render_crispy_form
from .processes import PROCESS_CREATE, PROCESS_VIEW, PROCESS_EDIT, process_title
from .fields import FieldOptions


class CrispyFormMixin:
    Meta: object
    fields: list
    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 col-lg-6 input-group-sm'
    submit_class = 'btn-success modal-submit'
    cancel_class = 'btn-secondary modal-cancel'
    delete_class = 'btn-danger modal-delete'
    edit_class = 'btn-warning modal-edit'

    def get_defaults(self, variable):
        result = self.supplied_kwargs.get(variable)
        if result is None and hasattr(self, 'Meta'):
            result = getattr(self.Meta, variable, None)
        return result

    def __init__(self, *args, pk=None, no_buttons=None, read_only=False, modal_title=None, form_delete=None,
                 form_setup=None, slug=None, request_user=None, form_id=None, edit_button=False, auto_placeholder=None,
                 **kwargs):
        self.supplied_kwargs = locals()
        self.auto_placeholder = self.get_defaults('auto_placeholder')
        self.no_buttons = self.get_defaults('no_buttons')
        self.read_only = self.get_defaults('read_only')
        self.modal_title = self.get_defaults('modal_title')
        self.form_delete = self.get_defaults('form_delete')
        self._form_id = self.get_defaults('form_id')
        self.edit_button = self.get_defaults('edit_button')
        self.user = request_user
        self.slug = slug
        self.form_setup = form_setup
        self.pk = pk
        self.instance = None
        self.helper = None
        self.buttons = []
        super().__init__(*args, **kwargs)
        self.setup_modal(*args, **kwargs)
        self.mode = []

    @property
    def form_id(self):
        if self._form_id:
            return self._form_id
        else:
            return self.__class__.__name__

    def post_init(self, *args, **kwargs):
        if self.form_setup:
            return self.form_setup(self, *args, **kwargs)

    def submit_button(self, css_class=submit_class, button_text='Submit'):
        return self.button(button_text, 'post_modal', css_class)

    def delete_button(self, css_class=delete_class):
        if self.instance.pk is not None:
            return self.button('Delete', {'function': 'post_modal', 'button': 'delete'}, css_class)

    def cancel_button(self, css_class=cancel_class):
        return self.button('Cancel', 'close', css_class)

    def view_edit_button(self, css_class=edit_class):
        return self.button('Edit', {'function': 'post_modal', 'button': {'button': 'refresh_modal', 'edit': True}},
                           css_class)

    def button(self, title, commands, css_class, **kwargs):
        if self.no_buttons:
            return HTML('')
        else:
            if type(commands) == str:
                params = [{'function': commands}]
            elif type(commands) == dict:
                params = [commands]
            else:
                params = commands
            return StrictButton(
                title,
                onclick=mark_safe('django_modal.process_commands_lock(' + json.dumps(params).replace('"', "'") + ')'),
                css_class=css_class, **kwargs
            )

    def get_title(self):

        if self.modal_title is None:
            if hasattr(self, 'Meta') and hasattr(self.Meta, 'model'):
                # noinspection PyProtectedMember
                # noinspection PyUnresolvedReferences
                model_name = self.Meta.model._meta.verbose_name.title()
            else:
                model_name = ''
            self.modal_title = [f'{t} {model_name}' for t in [
                process_title[PROCESS_CREATE], process_title[PROCESS_EDIT], process_title[PROCESS_VIEW]
            ]]
        if isinstance(self.modal_title, list):
            if self.instance.pk is None:
                return mark_safe(self.modal_title[0])
            elif self.read_only and len(self.modal_title) > 2:
                return mark_safe(self.modal_title[2])
            else:
                return mark_safe(self.modal_title[1])
        else:
            return mark_safe(self.modal_title)

    def label(self, text):
        return Div(HTML(text), css_class=self.label_class)

    @staticmethod
    def row(*args):
        return Div(*args, css_class='form-group row')

    def field_section(self, *args):
        return Div(*args, css_class=self.field_class)

    def setup_modal(self, *args, **kwargs):
        self.helper = FormHelper(self)
        self.helper.form_id = self.form_id
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = self.label_class
        self.helper.field_class = self.field_class
        self.helper.disable_csrf = True
        layout = self.post_init(*args, **kwargs)
        if layout:
            if isinstance(layout, (tuple, list)):
                self.helper.layout = Layout(*layout)
            else:
                self.helper.layout = Layout(layout)
        else:
            self.helper.layout = Layout(*[getattr(self.fields[f].widget, 'crispy_field_class', FieldOptions)
                                          (f, **getattr(self.fields[f].widget, 'crispy_kwargs', {}))
                                          for f in self.fields])
        existing_buttons = [b.content for b in self.helper.layout.fields if isinstance(b, StrictButton)]
        if not existing_buttons and not self.no_buttons and not self.buttons:
            if not self.read_only:
                self.buttons.append(self.submit_button())
            elif self.edit_button:
                self.buttons.append(self.view_edit_button())
            if self.form_delete and not self.read_only:
                self.buttons.append(self.delete_button())
            self.buttons.append(self.cancel_button())
        if self.buttons:
            self.append_buttons(self.buttons)
        if self.read_only:
            self.helper[:].update_attributes(disabled=True)

    def append_buttons(self, buttons):
        self.helper.layout.append(Div(Div(*buttons, css_class='btn-group'), css_class='form-buttons'))

    def clear_errors(self):
        # noinspection PyAttributeOutsideInit
        self._errors = {}

    def __str__(self):
        return mark_safe(render_crispy_form(self))


class ModelCrispyForm(CrispyFormMixin, forms.ModelForm):

    @classmethod
    def get_model(cls, initial=None):
        if initial is not None and 'app' in initial:
            return apps.get_model(initial.get('app'), initial.get('class'))
        else:
            # noinspection PyUnresolvedReferences
            return cls.Meta.model


class CrispyForm(CrispyFormMixin, forms.Form):
    pass
