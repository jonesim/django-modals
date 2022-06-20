from django.forms import ChoiceField
from django.forms.utils import pretty_name
from crispy_forms.layout import Field, Div
from crispy_forms.utils import TEMPLATE_PACK


class Flex(Div):
    def __init__(self, *args, **kwargs):
        css_class = 'd-flex'
        if 'css_class' in kwargs:
            css_class = f'{css_class} {kwargs.pop("css_class")}'
        super().__init__(*args, css_class=css_class, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        form.mode.append('flex')
        flex_data = super().render(form, form_style, context, template_pack=TEMPLATE_PACK, flex_mode=True, **kwargs)
        form.mode.pop()
        return flex_data


class MultiFieldRow(Div):

    def __init__(self, label, *fields, form_show_labels=False, form_class='', wrapper_class='d-flex mr-2',
                 field_class='input-group-sm', **kwargs):
        self.label = label
        extra_classes = FieldEx.get_extra_classes(locals())
        self.kwargs = kwargs
        super().__init__(*fields, css_class='row')

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        form.mode = form.mode + ['no_labels', 'flex']
        self.fields = Label(self.label), Div(
            FieldEx(*self.fields),
            css_class=self.kwargs.get('css_class', form.helper.field_class) + ' d-flex'
        )
        render_result = super().render(form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs)
        form.mode = form.mode[:-2]
        return render_result


class Label:
    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.kwargs = kwargs

    def render(self, form, _form_style, _context, _template_pack=TEMPLATE_PACK, **_kwargs):
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


class FieldEx(Field):
    template = "%s/field.html"
    @staticmethod
    def get_extra_classes(kwargs):
        return {c: kwargs.pop(c) for c in ['label_class', 'field_class', 'form_class', 'form_show_labels',
                                           'wrapper_class'] if c in kwargs}

    def __init__(self, *args, auto_placeholder=None, prepended_text=None, appended_text=None, extra_context=None,
                 **kwargs):
        self.auto_placeholder = auto_placeholder
        self.prepended_text = prepended_text
        self.appended_text = appended_text
        self.extra_classes = self.get_extra_classes(kwargs)
        self.org_context = extra_context if extra_context else {}
        super().__init__(*args, **kwargs)

    def add_to_context(self, context, extra_context, check_override=False, **kwargs):
        for key in kwargs:
            if not check_override or key not in self.extra_classes:
                if key in context:
                    self.org_context[key] = context[key]
                    context[key] = kwargs[key]
                else:
                    extra_context[key] = kwargs[key]

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if self.auto_placeholder or (self.auto_placeholder is None and getattr(form.helper, 'auto_placeholder', False)):
            self.add_placeholders(self.fields, form.fields)
        if extra_context is None:
            extra_context = {}
        if 'flex' in form.mode:
            self.add_to_context(context, extra_context, check_override=True, form_class='', wrapper_class='d-flex',
                                label_class=form.helper.flex_label_class, field_class=form.helper.flex_field_class)
        if 'no_labels' in form.mode:
            self.add_to_context(context, extra_context, form_show_labels=False)
        extra_context.update(self.extra_classes)

        if self.prepended_text or self.appended_text:
            template = self.get_prepended_appended_template_name(template_pack)
            self.add_to_context(context, extra_context, input_size='input-group-sm',
                                crispy_prepended_text=self.prepended_text, crispy_appended_text=self.appended_text)
        else:
            template = self.get_template_name(template_pack)

        for k in self.org_context:
            context[k] = self.org_context[k]

        content = self.get_rendered_fields(
            form,
            form_style,
            context,
            template_pack,
            template=template,
            attrs=self.attrs,
            extra_context=extra_context,
            **kwargs,
        )
        return content

    @staticmethod
    def get_prepended_appended_template_name(template_pack):
        return "%s/layout/prepended_appended_text.html" % template_pack

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


class FieldNoLabel(MultiField):
    def __init__(self, *args, **kwargs):
        kwargs['label_class'] = 'd-none'
        kwargs['form_class'] = ''
        super().__init__(*args, **kwargs)


class ChoiceFieldExtra(ChoiceField):
    def valid_value(self, value):
        return True
