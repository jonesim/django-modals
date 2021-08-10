from django import template
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static
from ajax_helpers.templatetags.ajax_helpers import ajax_button

from django_modals.helper import show_modal as show_modal_helper, modal_buttons, \
    modal_button_method as modal_button_method_helper

register = template.Library()


@register.simple_tag
def show_modal(modal, *args, **kwargs):
    return mark_safe(show_modal_helper(modal, *args, **kwargs))


@register.simple_tag
def modal_delete(url_name, slug=None, text=None, **kwargs):
    if not text:
        text = modal_buttons['delete'] + ' Delete'
    return ajax_button(text, 'delete', url_name=url_name, url_args=[slug], css_class='btn btn-danger', **kwargs)


@register.simple_tag
def modal_button_method(title, method_name, **kwargs):
    return modal_button_method_helper(title, method_name, **kwargs)


def get_sources(static_path, cdn_path, js_filename, css_filename, cdn=False):
    if cdn:
        js = cdn_path + js_filename
        css = cdn_path + css_filename
    else:
        js = static(static_path + js_filename)
        css = static(static_path + css_filename)
    return mark_safe(f'<script src="{js}"></script> <link href="{css}" rel="stylesheet">')


@register.simple_tag
def modal_imports(library, cdn=False):

    if library == 'toggle':
        return get_sources(
            'django_modals/',
            'https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/',
            'js/bootstrap4-toggle.min.js',
            'css/bootstrap4-toggle.min.css',
            cdn
        )

    elif library == 'select2':
        return get_sources(
            'django_modals/',
            'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/',
            'js/select2.min.js',
            'css/select2.min.css',
            cdn
        )
