"""Native form-field rendering tags for django-modals.

Replaces the small slice of ``crispy_forms`` the package relied on for field
markup.  ``modal_field`` reproduces ``crispy_forms``' ``crispy_field`` tag: it
appends the widget's lowercased class name (via a converter table) plus any
explicit class passed in the template, then renders the bound field.  The
``is_*`` filters mirror the crispy filters of the same name so the vendored
Bootstrap 4 templates can branch on widget type.
"""
from django import forms, template
from django.conf import settings

register = template.Library()


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def is_radioselect(field):
    return isinstance(field.field.widget, forms.RadioSelect) and not isinstance(
        field.field.widget, forms.CheckboxSelectMultiple
    )


@register.filter
def is_select(field):
    return isinstance(field.field.widget, forms.Select)


@register.filter
def is_checkboxselectmultiple(field):
    return isinstance(field.field.widget, forms.CheckboxSelectMultiple)


@register.filter
def is_file(field):
    return isinstance(field.field.widget, forms.FileInput)


@register.filter
def optgroups(field):
    """Render help for option-group fields (radio/checkbox-multiple); mirrors
    crispy_forms' ``optgroups`` filter."""
    id_ = field.field.widget.attrs.get('id') or field.auto_id
    attrs = {'id': id_} if id_ else {}
    attrs = field.build_widget_attrs(attrs)
    values = field.field.widget.format_value(field.value())
    return field.field.widget.optgroups(field.html_name, values, attrs)


def _pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


class ModalFieldNode(template.Node):
    """Render a bound field, injecting the converter class name and any extra
    attributes, exactly as crispy_forms' ``CrispyFieldNode`` did."""

    def __init__(self, field, attrs):
        self.field = field
        self.attrs = attrs

    def render(self, context):
        # Nodes are shared across threads, so resolve/cache per render context.
        if self not in context.render_context:
            context.render_context[self] = (template.Variable(self.field), self.attrs)

        field, attrs = context.render_context[self]
        field = field.resolve(context)

        widgets = getattr(field.field.widget, 'widgets', [getattr(field.field.widget, 'widget', field.field.widget)])

        if isinstance(attrs, dict):
            attrs = [attrs] * len(widgets)

        converters = {
            'textinput': 'textinput textInput',
            'fileinput': 'fileinput fileUpload',
            'passwordinput': 'textinput textInput',
        }
        converters.update(getattr(settings, 'CRISPY_CLASS_CONVERTERS', {}))

        for widget, attr in zip(widgets, attrs):
            class_name = widget.__class__.__name__.lower()
            class_name = converters.get(class_name, class_name)
            css_class = widget.attrs.get('class', '')
            if css_class:
                if css_class.find(class_name) == -1:
                    css_class += ' %s' % class_name
            else:
                css_class = class_name
            widget.attrs['class'] = css_class

            for attribute_name, attribute in attr.items():
                attribute_name = template.Variable(attribute_name).resolve(context)
                attributes = template.Variable(attribute).resolve(context)
                if attribute_name in widget.attrs:
                    for a in attributes.split():
                        if a not in widget.attrs[attribute_name].split():
                            widget.attrs[attribute_name] += ' ' + a
                else:
                    widget.attrs[attribute_name] = attributes

        return str(field)


@register.tag(name='modal_field')
def modal_field(parser, token):
    """{% modal_field field 'class' 'form-control' %}"""
    token = token.split_contents()
    field = token.pop(1)
    token.pop(0)
    attrs = {attribute_name: value for attribute_name, value in _pairwise(token)}
    return ModalFieldNode(field, attrs)
