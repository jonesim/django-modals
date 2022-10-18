import json
from django import forms
from django.apps import apps
from django.utils.safestring import mark_safe

from crispy_forms.layout import HTML, Layout, Div
from crispy_forms.bootstrap import StrictButton
from crispy_forms.utils import render_crispy_form
from .form_helpers import HorizontalHelper
from .processes import PROCESS_VIEW, PROCESS_EDIT_DELETE, PROCESS_VIEW_EDIT, PROCESS_DELETE, process_data
from .fields import FieldEx


class CrispyFormMixin:
    Meta: object
    fields: dict
    submit_class = 'btn-success modal-submit'
    cancel_class = 'btn-secondary modal-cancel'
    delete_class = 'btn-danger modal-delete'
    edit_class = 'btn-warning modal-edit'

    def get_defaults(self, variable):
        result = self.supplied_kwargs.get(variable)
        if result is None and hasattr(self, 'Meta'):
            result = getattr(self.Meta, variable, None)
        return result

    def __init__(self, *args, pk=None, no_buttons=None, modal_title=None, form_setup=None, slug=None,
                 request_user=None, form_id=None, process=None, layout_field_params=None, layout_field_classes=None,
                 helper_class=HorizontalHelper, progress_bar=None, header_html=None, clean=None, **kwargs):
        self.supplied_kwargs = locals()
        self.no_buttons = self.get_defaults('no_buttons')
        self.modal_title = self.get_defaults('modal_title')
        self._form_id = self.get_defaults('form_id')
        self.progress_bar = self.get_defaults('progress_bar')

        self.user = request_user
        self.slug = slug
        self.form_setup = form_setup
        self.pk = pk
        self.instance = None
        self.helper = None
        self.buttons = []
        self.helper_class = helper_class
        self.process = process
        self.layout_field_params = self.get_defaults('layout_field_params')
        # self.mode used when rendering fields e.g in flex divs
        self.mode = []
        self.triggers = {}
        self.trigger_fields = {}
        self.header_html = [HTML(header_html)] if header_html else []
        self._clean_method = clean
        self.html_above_buttons = ''
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

    def submit_button(self, css_class=submit_class, button_text='Submit', **kwargs):
        if self.progress_bar:
            return self.button('submit', {'function': 'post_modal',
                                          'options': {'progress': {'selector': f'#file_progress_bar'}}}, css_class,
                               **kwargs)
        else:
            return self.button(button_text, 'post_modal', css_class, **kwargs)

    def delete_button(self, css_class=delete_class, **kwargs):
        if self.instance.pk is not None:
            return self.button('Delete', {'function': 'post_modal', 'button': 'delete'}, css_class, **kwargs)

    def cancel_button(self, css_class=cancel_class, **kwargs):
        return self.button('Cancel', 'close', css_class, **kwargs)

    def view_edit_button(self, css_class=edit_class, **kwargs):
        return self.button('Edit', {'function': 'post_modal', 'button': 'make_edit'}, css_class, **kwargs)

    def button(self, title, commands, css_class, font_awesome=None, **kwargs):
        if self.no_buttons:
            return HTML('')
        else:
            if font_awesome:
                title = f'<i class="{font_awesome}"></i> {title}'
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
            return mark_safe(f'{process_data[self.process].modal_title} {model_name}')
        if isinstance(self.modal_title, list):
            if self.instance.pk is None:
                return mark_safe(self.modal_title[0])
            elif self.process in [PROCESS_VIEW, PROCESS_VIEW_EDIT] and len(self.modal_title) > 2:
                return mark_safe(self.modal_title[2])
            else:
                return mark_safe(self.modal_title[1])
        else:
            return mark_safe(self.modal_title)

    def label(self, text):
        return Div(HTML(text), css_class=self.helper.label_class)

    @staticmethod
    def row(*args):
        return Div(*args, css_class='form-group row')

    def field_section(self, *args):
        return Div(*args, css_class=self.helper.field_class)

    def format_layout_fields(self, *layout_fields):
        if len(layout_fields) == 1 and isinstance(layout_fields[0], (list, tuple)):
            layout_fields = layout_fields[0]
        fields = []
        for f in layout_fields:
            if isinstance(f, str):
                field_args = {}
                if self.layout_field_params and f in self.layout_field_params:
                    field_args.update(self.layout_field_params[f])
                field_args.update(getattr(self.fields[f].widget, 'crispy_kwargs', {}))
                # Class can be set in widget otherwise use FieldEx
                fields.append(getattr(self.fields[f].widget, 'crispy_field_class', FieldEx)(f, **field_args))
            else:
                fields.append(f)
        self.helper.layout = Layout(*self.header_html, *fields)

    def setup_modal(self, *args, **kwargs):
        self.helper = self.helper_class(self)
        self.helper.form_id = self.form_id
        layout = self.post_init(*args, **kwargs)
        if self.layout_field_params:
            for a in self.layout_field_params:
                if 'required' in self.layout_field_params[a]:
                    self.fields[a].required = self.layout_field_params[a].pop('required')
        if layout:
            if isinstance(layout, (tuple, list)):
                self.format_layout_fields(*layout)
            else:
                self.helper.layout = Layout(layout)
        else:
            self.format_layout_fields(*self.fields.keys())
        if getattr(self.helper, 'fields_wrap_class', None):
            # noinspection PyUnresolvedReferences
            self.helper[:].wrap_together(Div, css_class=self.helper.fields_wrap_class)
        existing_buttons = [b.content for b in self.helper.layout.fields if isinstance(b, StrictButton)]
        if not existing_buttons and not self.no_buttons and not self.buttons:
            if self.process not in [PROCESS_VIEW, PROCESS_VIEW_EDIT]:
                self.buttons.append(self.submit_button())
            elif self.process == PROCESS_VIEW_EDIT:
                self.buttons.append(self.view_edit_button())
            if self.process in [PROCESS_EDIT_DELETE, PROCESS_DELETE]:
                self.buttons.append(self.delete_button())
            self.buttons.append(self.cancel_button())
        self.helper.layout.append(HTML(self.html_above_buttons))
        if self.buttons:
            self.append_buttons(self.buttons)
        if self.process in [PROCESS_VIEW, PROCESS_VIEW_EDIT]:
            self.helper[:].update_attributes(disabled=True)

    def append_buttons(self, buttons):
        self.helper.layout.append(Div(Div(*buttons, css_class='btn-group'), css_class='form-buttons'))

    def clear_errors(self):
        # noinspection PyAttributeOutsideInit
        self._errors = {}

    def add_trigger(self, field, trigger, conditions):
        self.triggers[field] = conditions
        self.trigger_fields.setdefault(field, []).append(trigger)

    def reorder_fields(self, *key_order):
        if len(key_order) == 1 and isinstance(key_order[0], (list, tuple)):
            key_order = key_order[0]
        self.fields = {k: self.fields[k] for k in key_order}

    def clean(self):
        cleaned_data = super().clean()
        if self._clean_method:
            self._clean_method(self, cleaned_data)
        return cleaned_data

    def __str__(self):
        if self.triggers:
            for f, triggers in self.trigger_fields.items():
                for t in triggers:
                    self.helper[f].update_attributes(**{t: 'django_modal.alter_form(this, arguments[0])'})
            self.helper.layout.append(HTML(f'''<script>
                $(document).off("modalPostLoad");
                $(document).on("modalPostLoad",function(){{
                django_modal.modal_triggers.{self.form_id}={json.dumps(self.triggers)};
                django_modal.reset_triggers(\'{self.form_id}\')}})
                </script>'''))
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
