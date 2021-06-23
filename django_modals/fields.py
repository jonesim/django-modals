from django.forms import ChoiceField, MultipleChoiceField
from crispy_forms.layout import Field, HTML, Div
from crispy_forms.utils import TEMPLATE_PACK
from crispy_forms.bootstrap import PrependedText, AppendedText, PrependedAppendedText

date_picker = {'autocomplete': 'off', 'css_class': 'datepicker', 'style': 'width:110px'}


def field_select2(*args):
    return Field(*args, css_class='s2-enable', style='width:100%')


def html_label(title):
    return Div(Div(HTML(title), css_class='col-form-label form-control-sm'), css_class='col-md-3')


def toggle(field, options, **_kwargs):
    return Field(field, data_toggle="toggle", data_size="small", data_on=options[0], data_off=options[1])


class FieldToggle(Field):

    def __init__(self, *args, **kwargs):
        kwargs['data_toggle'] = 'toggle'
        kwargs['data_size'] = 'small'
        options = kwargs.pop('options', ('On', 'Off'))
        kwargs['data_on'] = options[0]
        kwargs['data_off'] = options[1]
        super().__init__(*args, **kwargs)


def reverse_field(*args, field_class='form-group-sm', **kwargs):
    return FieldOptions(*args, css_class='form-control-sm', field_class=field_class, group_class='d-flex',
                        label_class='form-control-sm', **kwargs, template='modal_fields/reverse.html')


def multi_row(label, row):
    return Div(
        html_label(label),
        Div(Div(*row, css_class='d-flex')),
        css_class="row form-group multi-field")


class AddFieldClassOptionsMixin:

    def __init__(self, *args, **kwargs):
        self.extra_classes = {c: kwargs.pop(c) for c in ['label_class', 'field_class', 'form_class'] if c in kwargs}
        super().__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if extra_context is None:
            extra_context = {}
        extra_context.update(self.extra_classes)
        # noinspection PyUnresolvedReferences
        return super().render(form, form_style, context, template_pack, extra_context, **kwargs)


class FieldOptions(AddFieldClassOptionsMixin, Field):
    pass


class PrependedTextOptions(AddFieldClassOptionsMixin, PrependedText):
    pass


class AppendedTextOptionsMixin(AddFieldClassOptionsMixin, AppendedText):
    pass


class PrependedAppendedTextOptions(AddFieldClassOptionsMixin, PrependedAppendedText):
    pass


class MultiField(FieldOptions):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_class', 'col-form-label-sm')
        kwargs.setdefault('field_class', 'input-group-sm mr-2')
        kwargs.setdefault('wrapper_class', 'mb-0')
        if 'width' in kwargs:
            kwargs['style'] = f'width:{kwargs.pop("width")}px'
        super().__init__(*args, **kwargs)


class FieldNoLabel(MultiField):
    def __init__(self, *args, **kwargs):
        kwargs['label_class'] = 'd-none'
        kwargs['form_class'] = ''
        super().__init__(*args, **kwargs)


class MultipleChoiceFieldExtra(MultipleChoiceField):

    def valid_value(self, value):
        return True


class ChoiceFieldExtra(ChoiceField):
    def valid_value(self, value):
        return True
