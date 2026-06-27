from django.forms import ChoiceField
from django.forms.utils import pretty_name
from django.utils.html import conditional_escape

from .layout import Div, render_field

EXTRA_CLASS_KEYS = ['label_class', 'field_class', 'form_class', 'form_show_labels', 'wrapper_class']


class MultiFieldRow(Div):

    def __init__(self, label, *fields, form_show_labels=False, form_class='', wrapper_class='d-flex mr-2',
                 field_class='input-group-sm', **kwargs):
        self.label = label
        self.row_fields = list(fields)
        self.kwargs = kwargs
        super().__init__(css_class='row')

    def render(self, form, context):
        form.mode = form.mode + ['no_labels', 'flex']
        self.fields = [Label(self.label), Div(
            FieldEx(*self.row_fields),
            css_class=self.kwargs.get('css_class', form.helper.field_class) + ' d-flex'
        )]
        render_result = super().render(form, context)
        form.mode = form.mode[:-2]
        return render_result


class Label:
    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.kwargs = kwargs

    def render(self, form, context):
        if 'css_class' in self.kwargs:
            css_class = self.kwargs['css_class']
        else:
            css_class = form.helper.label_class
        if 'form-horizontal' in form.helper.form_class:
            css_class += ' col-form-label'
        labels = ''
        if 'style' in self.kwargs:
            style = f' style="{self.kwargs["style"]}"'
        else:
            style = ''
        for f in self.fields:
            if f not in form.fields:
                label = f
            else:
                label = form.fields[f].label
                if label is None:
                    label = f
            labels += f'<div{style} class="{css_class}">{label}</div>'
        return labels


class FieldEx:
    """Layout spec for one or more form fields.

    Native replacement for the crispy ``Field`` subclass.  Holds field name(s),
    HTML attributes, the per-field class overrides (``label_class`` etc.) and
    optional prepended/appended input-group text.  ``render`` emits the field
    template for each named field.
    """

    template = 'django_modals/forms/bootstrap4/field.html'

    @staticmethod
    def get_extra_classes(kwargs):
        return {c: kwargs.pop(c) for c in EXTRA_CLASS_KEYS if c in kwargs}

    def __init__(self, *args, auto_placeholder=None, prepended_text=None, appended_text=None, extra_context=None,
                 **kwargs):
        self.fields = list(args)
        self.auto_placeholder = auto_placeholder
        self.prepended_text = prepended_text
        self.appended_text = appended_text
        self.extra_classes = self.get_extra_classes(kwargs)
        self.org_context = extra_context if extra_context else {}
        self.attrs = {}
        if 'css_class' in kwargs:
            self.attrs['class'] = kwargs.pop('css_class')
        if 'template' in kwargs:
            self.template = kwargs.pop('template')
        self.attrs.update({k.replace('_', '-'): conditional_escape(v) for k, v in kwargs.items()})

    def update_attributes(self, **kwargs):
        self.attrs.update({k.replace('_', '-'): v for k, v in kwargs.items()})

    def get_prepended_appended_template_name(self):
        return 'django_modals/forms/bootstrap4/prepended_appended_text.html'

    def render(self, form, context):
        if self.auto_placeholder or (self.auto_placeholder is None and context.get('auto_placeholder')):
            self.add_placeholders(self.fields, form.fields)

        extra_context = {}
        if 'flex' in form.mode:
            flex_defaults = {'form_class': '', 'wrapper_class': 'd-flex',
                             'label_class': form.helper.flex_label_class,
                             'field_class': form.helper.flex_field_class}
            for key, value in flex_defaults.items():
                if key not in self.extra_classes:
                    extra_context[key] = value
        if 'no_labels' in form.mode:
            extra_context['form_show_labels'] = False
        extra_context.update(self.extra_classes)
        extra_context.update(self.org_context)

        if self.prepended_text or self.appended_text:
            template = self.get_prepended_appended_template_name()
            extra_context.update(input_size='input-group-sm', prepended_text=self.prepended_text,
                                 appended_text=self.appended_text)
        else:
            template = self.template

        return ''.join(
            render_field(f, form, context, template=template, attrs=self.attrs, extra_context=extra_context)
            for f in self.fields
        )

    @staticmethod
    def add_placeholders(fields, form_fields):
        for f in fields:
            if type(f) == str:
                if not form_fields[f].label:
                    form_fields[f].widget.attrs['placeholder'] = pretty_name(f)
                else:
                    form_fields[f].widget.attrs['placeholder'] = form_fields[f].label


class MultiField(FieldEx):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_class', 'col-form-label-sm')
        kwargs.setdefault('field_class', 'input-group-sm mr-2')
        kwargs.setdefault('wrapper_class', 'mb-0')
        if 'width' in kwargs:
            kwargs['style'] = f'width:{kwargs.pop("width")}px'
        super().__init__(*args, **kwargs)


class ChoiceFieldExtra(ChoiceField):
    def valid_value(self, value):
        return True
