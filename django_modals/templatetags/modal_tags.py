from django import template
from django.utils.safestring import mark_safe
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
