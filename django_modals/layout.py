"""Native layout nodes + renderer that replace the slice of ``crispy_forms``
django-modals used to build form HTML.

A *layout* is an ordered tree of nodes (``Layout``/``Div``/``Fieldset``/``HTML``
and the field specs in ``fields.py``).  Every node implements
``render(form, context) -> str``; the renderer walks the tree joining the HTML.
``context`` is a plain dict seeded from the form's helper by
:func:`get_helper_context` (label/field classes, ``use_custom_control`` etc.) —
the same variables crispy injected via ``FormHelper.get_attributes``.
"""
import re

from django.template.loader import render_to_string
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

DEFAULT_FIELD_TEMPLATE = 'django_modals/forms/bootstrap4/field.html'


def flatatt(attrs):
    """Render a dict as HTML attributes, turning ``data_id`` into ``data-id``."""
    pairs = []
    for k, v in attrs.items():
        if v is False or v is None:
            continue
        name = k.replace('_', '-')
        if v is True:
            pairs.append(' %s' % name)
        else:
            pairs.append(' %s="%s"' % (name, conditional_escape(v)))
    return mark_safe(''.join(pairs))


def render_fields(fields, form, context):
    return ''.join(render_field(f, form, context) for f in fields)


def render_field(field, form, context, template=None, attrs=None, extra_context=None):
    """Render a single layout child.

    A child with a ``render`` method renders itself (nested layout objects); a
    string is treated as a field name, its widget attrs are updated and the
    field template is rendered — mirroring ``crispy_forms.utils.render_field``.
    """
    if field is None:
        return ''
    if hasattr(field, 'render'):
        return field.render(form, context)
    try:
        bound_field = form[field]
    except KeyError:
        return ''
    if attrs:
        bound_field.field.widget.attrs.update(attrs)
    ctx = dict(context)
    ctx['field'] = bound_field
    ctx['flat_attrs'] = flatatt(attrs) if attrs else ''
    if extra_context:
        ctx.update(extra_context)
    return render_to_string(template or DEFAULT_FIELD_TEMPLATE, ctx)


class HTML:
    """A raw HTML fragment in a layout."""

    def __init__(self, html):
        self.html = html

    def render(self, form, context):
        return str(self.html)


class Div:
    """Wraps its children in a ``<div>``."""

    css_class = None

    def __init__(self, *fields, css_class=None, css_id=None, **kwargs):
        self.fields = list(fields)
        if css_class:
            self.css_class = '%s %s' % (self.css_class, css_class) if self.css_class else css_class
        self.css_id = css_id
        self.attrs = kwargs

    def render(self, form, context):
        content = render_fields(self.fields, form, context)
        id_attr = ' id="%s"' % self.css_id if self.css_id else ''
        class_attr = ' class="%s"' % self.css_class if self.css_class else ''
        return mark_safe('<div%s%s%s>%s</div>' % (id_attr, class_attr, flatatt(self.attrs), content))


class Fieldset:
    """Wraps its children in a ``<fieldset>`` with an optional ``<legend>``."""

    def __init__(self, legend, *fields, css_class=None, **kwargs):
        self.legend = legend
        self.fields = list(fields)
        self.css_class = css_class

    def render(self, form, context):
        content = render_fields(self.fields, form, context)
        legend = '<legend>%s</legend>' % self.legend if self.legend else ''
        class_attr = ' class="%s"' % self.css_class if self.css_class else ''
        return mark_safe('<fieldset%s>%s%s</fieldset>' % (class_attr, legend, content))


class Layout:
    """Ordered container of layout nodes."""

    def __init__(self, *fields):
        self.fields = list(fields)

    def append(self, node):
        self.fields.append(node)

    def render(self, form, context):
        return render_fields(self.fields, form, context)


def get_helper_context(form):
    """Build the base render context from the form's helper config object —
    the variables the field templates expect (equivalent to crispy's
    ``FormHelper.get_attributes``)."""
    helper = form.helper
    label_class = getattr(helper, 'label_class', '') or ''
    form_class = getattr(helper, 'form_class', '') or ''
    context = {
        'form_class': form_class,
        'label_class': label_class,
        'field_class': getattr(helper, 'field_class', '') or '',
        'form_show_labels': getattr(helper, 'form_show_labels', True),
        'form_show_errors': getattr(helper, 'form_show_errors', True),
        'use_custom_control': getattr(helper, 'use_custom_control', True),
        'error_text_inline': getattr(helper, 'error_text_inline', True),
        'help_text_inline': getattr(helper, 'help_text_inline', False),
        'auto_placeholder': getattr(helper, 'auto_placeholder', False),
        'form_id': getattr(helper, 'form_id', None),
    }
    if getattr(helper, 'wrapper_class', None):
        context['wrapper_class'] = helper.wrapper_class
    if 'form-horizontal' in form_class.split():
        offsets = ['offset%s-%s' % (m[0], m[-1]) for m in re.findall(r'col(-(xl|lg|md|sm))?-(\d+)', label_class)]
        if offsets:
            context['bootstrap_checkbox_offsets'] = offsets
    return context
