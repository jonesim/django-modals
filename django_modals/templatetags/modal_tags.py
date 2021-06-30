from django import template
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
from django_modals.helper import show_modal as show_modal_helper

from django_modals import helper

register = template.Library()


@register.simple_tag
def onclick_modal(modal, *args):
    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    return mark_safe("django_modal.show_modal('{}')".format(reverse(modal, kwargs={'slug': slug})))


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
    return helper.button_javascript(button_name, url_name, url_args, **kwargs)
