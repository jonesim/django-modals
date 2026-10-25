"""Opt-in ``html_classes`` reimplementation of the Bootstrap field template,
configurable per CSS framework.

:func:`render_field_html` is a drop-in alternative to rendering
``django_modals/forms/bootstrap4/field.html`` via ``render_to_string``: it takes
the same context dict :func:`django_modals.layout.render_field` builds and emits
equivalent markup, assembled in Python with ``html_classes`` instead of the
template engine.

The control flow lives once in :class:`BootstrapFieldRenderer`; each framework is
a small subclass supplying its class-name tokens and the handful of structural
differences (Bootstrap 5 has no ``custom-control``/``custom-select``/``custom-file``
and drops ``form-group`` for spacing utilities).  The framework follows the
ecosystem-wide django-ajax-helpers setting::

    CSS_FRAMEWORK = 'bootstrap5'   # default 'bootstrap4'

We only ship Bootstrap 4 *templates*, so for any other framework the html_classes
renderer is used automatically (see :func:`use_renderer`); for Bootstrap 4 it stays
opt-in behind :data:`USE_HTML_CLASSES` so the template path and downstream template
overrides keep working unchanged.

Scope note: only the main field renderer is framework-aware.  The prepended/appended,
colour-picker and other widget templates are still Bootstrap 4 and would need their
own variants for a fully Bootstrap 5 project.
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from html_classes.html import HtmlDiv, HtmlLabel

from .templatetags.modal_forms import (
    apply_widget_classes, is_checkbox, is_checkboxselectmultiple, is_file, is_radioselect, is_select,
)

#: Force the html_classes renderer for the *default* (Bootstrap 4) framework.
#: For non-default frameworks the renderer is always used (no templates ship).
USE_HTML_CLASSES = False

ASTERISK = '<span class="asteriskField">*</span>'


def _invalid(base, field):
    return base + ' is-invalid' if field.errors else base


def _help_text(field, help_text_inline):
    if not field.help_text:
        return ''
    if help_text_inline:
        return f'<span id="hint_{field.auto_id}" class="text-muted">{field.help_text}</span>'
    return f'<small id="hint_{field.auto_id}" class="form-text text-muted">{field.help_text}</small>'


def _field_errors(field, form_show_errors, block):
    if not (form_show_errors and field.errors):
        return ''
    tag = 'p' if block else 'span'
    return ''.join(
        f'<{tag} id="error_{i}_{field.auto_id}" class="invalid-feedback"><strong>{error}</strong></{tag}>'
        for i, error in enumerate(field.errors, 1)
    )


def _help_and_errors(field, ctx):
    """Python equivalent of ``help_text_and_errors.html`` (framework-neutral)."""
    help_text_inline = ctx.get('help_text_inline', False)
    error_text_inline = ctx.get('error_text_inline', True)
    form_show_errors = ctx.get('form_show_errors', True)
    out = ''
    if help_text_inline and not error_text_inline:
        out += _help_text(field, help_text_inline)
    out += _field_errors(field, form_show_errors, block=not error_text_inline)
    if not help_text_inline:
        out += _help_text(field, help_text_inline)
    return out


class BootstrapFieldRenderer:
    """Token-driven field renderer.  Defaults reproduce Bootstrap 4; subclasses
    override the tokens that differ."""

    #: directory holding the delegated widget partials (radio / checkbox-multiple)
    template_dir = 'django_modals/forms/bootstrap4'

    group = 'form-group'                       # field wrapper utility
    plain_select = 'form-control'              # <select> when not a custom control
    plain_file = 'form-control-file'           # <input type=file> when not a custom control
    custom_select = 'custom-select'
    custom_file_template = 'django_modals/forms/bootstrap4/field_file.html'
    custom_checkbox = 'custom-control custom-checkbox'
    custom_checkbox_input = 'custom-control-input'
    custom_checkbox_label = 'custom-control-label'
    form_check = 'form-check'
    form_check_input = 'form-check-input'
    form_check_label = 'form-check-label'

    def effective_custom_control(self, ctx):
        """Whether the framework's custom-control styling applies for this field."""
        return ctx.get('use_custom_control', True)

    # -- helpers --------------------------------------------------------------
    def _label(self, field, required, radio, horizontal, label_class):
        cls = ' '.join(filter(None, ['col-form-label' if horizontal else '', label_class,
                                     'requiredField' if required else '']))
        attrs = {'for_': field.id_for_label} if field.id_for_label and not radio else {}
        return HtmlLabel(str(field.label) + (ASTERISK if required else ''),
                         css_classes=cls or None, **attrs).render()

    def _optgroup(self, field, ctx, name, custom):
        sub = dict(ctx)
        sub['use_custom_control'] = custom
        return render_to_string(f'{self.template_dir}/{name}.html', sub)

    def _control_class(self, field, custom):
        if is_select(field):
            return _invalid(self.custom_select if custom else self.plain_select, field)
        if is_file(field):
            return _invalid(self.plain_file, field)
        return _invalid('form-control', field)

    # -- entry point ----------------------------------------------------------
    def render(self, field, ctx):
        if field.is_hidden:
            return mark_safe(str(field))

        horizontal = 'form-horizontal' in (ctx.get('form_class') or '')
        label_class = ctx.get('label_class') or ''
        field_class = ctx.get('field_class') or ''
        wrapper_class = ctx.get('wrapper_class') or ''
        show_labels = ctx.get('form_show_labels', True)
        tag = ctx.get('tag') or 'div'
        required = field.field.required
        custom = self.effective_custom_control(ctx)

        checkbox = is_checkbox(field)
        radio = is_radioselect(field)
        multi = is_checkboxselectmultiple(field)
        group_class = self.group + (' row' if horizontal else '')

        if checkbox:
            main_class = self.custom_checkbox if custom else self.form_check
        else:
            main_class = group_class
        main_class = ' '.join(filter(None, [main_class, wrapper_class, field.css_classes()]))

        parts = []
        if field.label and not checkbox and show_labels:
            parts.append(self._label(field, required, radio, horizontal, label_class))

        if multi or radio:
            parts.append(self._optgroup(field, ctx, 'checkboxselectmultiple' if multi else 'radioselect', custom))
        elif checkbox and show_labels:
            input_class = self.custom_checkbox_input if custom else self.form_check_input
            parts.append(apply_widget_classes(field, {'class': _invalid(input_class, field)}))
            label_class_cb = self.custom_checkbox_label if custom else self.form_check_label
            if required:
                label_class_cb += ' requiredField'
            parts.append(HtmlLabel(str(field.label) + (ASTERISK if required else ''),
                                   css_classes=label_class_cb, for_=field.id_for_label).render())
            parts.append(_help_and_errors(field, ctx))
        elif is_file(field) and custom and self.custom_file_template:
            parts.append(render_to_string(self.custom_file_template, ctx))
        else:
            inner = apply_widget_classes(field, {'class': self._control_class(field, custom)})
            parts.append(HtmlDiv(inner + _help_and_errors(field, ctx), css_classes=field_class or None).render())

        main = HtmlDiv(''.join(parts), css_classes=main_class, element=tag, id=f'div_{field.auto_id}').render()

        if checkbox:
            if label_class:
                offsets = ''.join(f'{o} ' for o in ctx.get('bootstrap_checkbox_offsets', []))
                main = HtmlDiv(main, css_classes=(offsets + field_class).strip() or None).render()
            main = HtmlDiv(main, css_classes=group_class).render()

        return mark_safe(main)


class Bootstrap4Renderer(BootstrapFieldRenderer):
    """Default — identical to the Bootstrap 4 field template."""


class Bootstrap5Renderer(BootstrapFieldRenderer):
    """Bootstrap 5: no custom controls, ``form-select``, native file input,
    ``mb-3`` spacing instead of ``form-group``."""

    group = 'mb-3'
    plain_select = 'form-select'
    plain_file = 'form-control'
    custom_file_template = None

    def effective_custom_control(self, ctx):
        return False  # Bootstrap 5 has no custom-control styling


_RENDERERS = {
    'bootstrap4': Bootstrap4Renderer,
    'bootstrap5': Bootstrap5Renderer,
}
_renderer_cache = {}


try:
    from ajax_helpers.config import get_css_framework
except ImportError:
    # django-ajax-helpers < 1.0.0 has no config module; read the same setting directly
    def get_css_framework():
        return getattr(settings, 'CSS_FRAMEWORK', 'bootstrap4')


def get_renderer():
    name = get_css_framework()
    if name not in _renderer_cache:
        renderer_class = _RENDERERS.get(name)
        if renderer_class is None:
            raise ImproperlyConfigured(
                f"CSS_FRAMEWORK={name!r} is not supported; choose one of {sorted(_RENDERERS)}")
        _renderer_cache[name] = renderer_class()
    return _renderer_cache[name]


def use_renderer():
    """The html_classes renderer is used when explicitly enabled, or whenever the
    selected framework isn't the one we ship templates for (Bootstrap 4)."""
    return USE_HTML_CLASSES or get_css_framework() != 'bootstrap4'


def render_field_html(field, ctx):
    return get_renderer().render(field, ctx)
