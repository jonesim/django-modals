import json
from django import forms
from django.apps import apps
from django.template.loader import render_to_string
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Field, Layout
from crispy_forms.bootstrap import StrictButton


class CrispyFormMixin:

    instance = None

    def post_init(self, *args, **kwargs):
        if self.modal_config.get('form_setup'):
            return self.modal_config['form_setup'](self, *args, **kwargs)
        pass

    def submit_button(self, **kwargs):
        return self.button(kwargs.get('button_text', 'Submit'),
                           [{'function': 'post_modal'}],
                           kwargs.get('css_class', 'btn-primary'))

    def delete_button(self, **_kwargs):
        if self.instance.pk is not None:
            return self.button('Delete', [{'function': 'post_modal', 'button_name': 'delete'}], "btn-danger")

    def cancel_button(self):
        function_params = [{'function': 'close'}]
        return self.button('Cancel', function_params, "btn")

    def button(self, title, commands, css_class, **kwargs):
        if self.no_buttons:
            return HTML('')
        else:
            params = commands
            return StrictButton(title, onclick='modal.process_commands_lock(' + json.dumps(params) + ')',
                                css_class=css_class, **kwargs)

    def remove_kwargs(self, kwargs):
        self.modal_config = kwargs.pop('modal_config', {})
        self.no_buttons = kwargs.pop('no_buttons', False)
        self.pk = kwargs.pop('pk', None)
        self.readonly = kwargs.pop('readonly', False)
        # self.url = kwargs.pop('url', None)
        if 'modal_title' in self.modal_config:
            self.modal_title = self.modal_config['modal_title']
        if 'form_delete' in self.modal_config:
            self.Meta.delete = self.modal_config['form_delete']

    def set_title(self):
        if hasattr(self, 'modal_title'):
            title = self.modal_title
        elif hasattr(self.Meta, 'modal_title'):
            title = self.Meta.modal_title
        else:
            title = ''
        if isinstance(title, list):
            if self.instance.pk is None:
                self.modal_title = title[0]
            else:
                self.modal_title = title[1]
        else:
            self.modal_title = title

    def setup_modal(self, *args, **kwargs):
        self.set_title()
        self.helper = FormHelper(self)
        if not hasattr(self.Meta, 'form_id'):
            self.Meta.form_id = self.helper.form_id = self.__class__.__name__
        self.helper.form_id = self.Meta.form_id
        self.helper.form_group_wrapper_class = 'mb-2'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3 col-form-label-sm'
        self.helper.field_class = 'col-md-9 col-lg-6 input-group-sm'
        for f in self.fields:
            if type(self.fields[f]) == forms.models.ModelChoiceField:
                self.fields[f].empty_label = ' '
        self.helper.layout = Layout()
        layout = self.post_init(*args, **kwargs)
        if layout:
            self.helper.layout.extend(layout)
        if not self.helper.layout:
            self.helper.layout = Layout(Field(*self.fields))
        existing_buttons = [b.content for b in self.helper.layout.fields if isinstance(b, StrictButton)]
        if not existing_buttons and not hasattr(self.Meta, 'no_buttons'):
            self.helper.layout.append(self.submit_button(css_class="btn-success"))
            if hasattr(self.Meta, 'delete') and self.Meta.delete:
                self.helper.layout.append(self.delete_button())
            self.helper.layout.append(self.cancel_button())
        self.helper.layout.append(HTML(render_to_string('form_scripts/form_change.html', {'form_helper': self.helper})))


class ModelCrispyForm(CrispyFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.remove_kwargs(kwargs)
        super().__init__(*args, **kwargs)
        self.setup_modal(*args, **kwargs)

    @classmethod
    def get_model(cls, initial=None):
        if initial is not None and 'app' in initial:
            return apps.get_model(initial.get('app'), initial.get('class'))
        else:
            return cls.Meta.model

    def clear_errors(self):
        self._errors = {}

    def full_clean(self):
        ret_val = super().full_clean()
        return ret_val


class CrispyForm(CrispyFormMixin, forms.Form):

    def __init__(self, *args, **kwargs):
        self.remove_kwargs(kwargs)
        super(CrispyForm, self).__init__(*args, **kwargs)
        self.setup_modal(*args, **kwargs)
