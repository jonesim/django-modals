from django import template
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe

from ajax_helpers.templatetags.ajax_helpers import ajax_button

from django_modals.helper import show_modal as show_modal_helper, modal_buttons, button_javascript

register = template.Library()


@register.simple_tag
def modal_url(modal, *args):
    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    return mark_safe(format(reverse(modal, kwargs={'slug': slug})))


@register.simple_tag
def show_modal(modal, *args, **kwargs):
    return mark_safe(show_modal_helper(modal, *args, **kwargs))


@register.simple_tag
def submit_form(url_name, *args):
    """
        Used by to submit a form on a page rather than a modal
    """
    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    url = reverse(url_name, kwargs={'slug': slug})
    view = resolve(url).func.view_class
    return mark_safe(f"ajax_helpers.send_form('{url}?formonly=true&no_buttons=True', '{view.form_class.__name__}')")


@register.simple_tag
def modal_button(button_name, url_name=None, url_args=None, **kwargs):
    return button_javascript(button_name, url_name, url_args, **kwargs)


@register.simple_tag
def modal_delete(url_name, slug=None, text=None, **kwargs):
    if not text:
        text = modal_buttons['delete'] + ' Delete'
    return ajax_button(text, 'delete', url_name=url_name, url_args=[slug], css_class='btn btn-danger', **kwargs)
