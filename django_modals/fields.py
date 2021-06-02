from django.forms import ChoiceField, MultipleChoiceField
from crispy_forms.layout import Field, HTML, Div
from crispy_forms.utils import TEMPLATE_PACK


date_picker = {'autocomplete': 'off', 'css_class': 'datepicker', 'style': 'width:110px'}


def field_select2(*args):
    return Field(*args, css_class='s2-enable', style='width:100%')


def html_label(title):
    return Div(Div(HTML(title), css_class='col-form-label form-control-sm'), css_class='col-md-3')


def toggle(field, options, **kwargs):
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
    return FieldBootStrap(*args, css_class='form-control-sm', field_class=field_class, group_class='d-flex',
                          label_class='form-control-sm', **kwargs, template='modal_fields/reverse.html')


def multi_row(label, row):
    return Div(
        html_label(label),
        Div(Div(*row, css_class='d-flex'), css_class='col-md-9 col-lg-6'),
        css_class="row form-group multi-field")


class FieldBootStrap(Field):

    def __init__(self, *args, **kwargs):
        self.label_class = kwargs.pop('label_class', None)
        self.field_class = kwargs.pop('field_class', None)
        self.group_class = kwargs.pop('group_class', None)

        super().__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if extra_context is None:
            extra_context = {}
        if self.label_class is not None:
            extra_context['label_class'] = self.label_class
        if self.field_class is not None:
            extra_context['field_class'] = self.field_class
        if self.group_class:
            extra_context['group_class'] = self.group_class
        return super().render(form, form_style, context, template_pack, extra_context, **kwargs)


class MultiField(FieldBootStrap):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_class = kwargs.pop('label_class', 'px-1')
        self.field_class = kwargs.pop('field_class', 'input-group-sm')
        self.group_class = kwargs.pop('group_class', 'form-group mb-0')


class FieldNoLabel(FieldBootStrap):
    def __init__(self, *args, **kwargs):
        if 'label_class' not in kwargs:
            kwargs['label_class'] = 'd-none'
        if 'field_class' not in kwargs:
            kwargs['field_class'] = 'input-group-sm'
        if 'group_class' not in kwargs:
            kwargs['group_class'] = 'dummy'
        if 'width' in kwargs:
            kwargs['style'] = "width:" + str(kwargs['width']) + "px"
        super(FieldNoLabel, self).__init__(*args, **kwargs)


class MultipleChoiceFieldExtra(MultipleChoiceField):

    def valid_value(self, value):
        return True


class ChoiceFieldExtra(ChoiceField):
    def valid_value(self, value):
        return True
