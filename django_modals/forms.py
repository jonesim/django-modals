import json
from django import forms
from django.apps import apps
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout, Div
from crispy_forms.bootstrap import StrictButton


class CrispyFormMixin:
    Meta: object
    fields: list

    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 col-lg-6 input-group-sm'
    submit_class = 'btn-success modal-submit'
    cancel_class = 'btn-secondary modal-cancel'
    delete_class = 'btn-danger modal-delete'

    def get_defaults(self, variable):
        result = self.supplied_kwargs.get(variable)
        if result is None:
            result = getattr(self.Meta, variable, None)
        return result

    def __init__(self, *args, pk=None, no_buttons=None, read_only=False, modal_title=None, form_delete=None,
                 form_setup=None, slug=None, user=None, form_id=None, **kwargs):
        self.supplied_kwargs = locals()
        self.no_buttons = self.get_defaults('no_buttons')
        self.read_only = self.get_defaults('read_only')
        self.modal_title = self.get_defaults('modal_title')
        self.form_delete = self.get_defaults('form_delete')
        self._form_id = self.get_defaults('form_id')
        self.user = user
        self.slug = slug
        self.form_setup = form_setup
        self.pk = pk
        self.instance = None
        self.helper = None
        super().__init__(*args, **kwargs)
        self.setup_modal(*args, **kwargs)

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
            return StrictButton(title, onclick='django_modal.process_commands_lock(' + json.dumps(params) + ')',
                                css_class=css_class, **kwargs)

    def get_title(self):
        if isinstance(self.modal_title, list):
            if self.instance.pk is None:
                return mark_safe(self.modal_title[0])
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
        for f in self.fields:
            if type(self.fields[f]) == forms.models.ModelChoiceField:
                self.fields[f].empty_label = ' '
        layout = self.post_init(*args, **kwargs)
        if layout:
            if isinstance(layout, (tuple, list)):
                self.helper.layout = Layout(*layout)
            else:
                self.helper.layout = Layout(layout)
        else:
            self.helper.layout = Layout(Field(*self.fields))
        existing_buttons = [b.content for b in self.helper.layout.fields if isinstance(b, StrictButton)]
        if not existing_buttons and not self.no_buttons:
            buttons = [self.submit_button()]
            if self.form_delete:
                buttons.append(self.delete_button())
            buttons.append(self.cancel_button())
            self.helper.layout.append(Div(Div(*buttons, css_class='btn-group'), css_class='form-buttons'))
        if self.read_only:
            self.helper[:].update_attributes(disabled=True)
        self.helper.layout.append(HTML(render_to_string('form_scripts/form_change.html', {'form_helper': self.helper})))


class ModelCrispyForm(CrispyFormMixin, forms.ModelForm):

    @classmethod
    def get_model(cls, initial=None):
        if initial is not None and 'app' in initial:
            return apps.get_model(initial.get('app'), initial.get('class'))
        else:
            # noinspection PyUnresolvedReferences
            return cls.Meta.model

    def clear_errors(self):
        self._errors = {}


class CrispyForm(CrispyFormMixin, forms.Form):
    pass
