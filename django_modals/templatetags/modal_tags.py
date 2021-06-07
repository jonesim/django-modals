from django import template
from django.urls import reverse, resolve
from django.utils.safestring import mark_safe
from django_modals.helper import show_modal as show_modal_helper, post_data_tag

register = template.Library()


@register.simple_tag
def onclick_modal(modal, *args):
    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    return mark_safe("modal.show_modal('{}')".format(reverse(modal, kwargs={'slug': slug})))


@register.simple_tag
def modal_url(modal, *args):
    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    return mark_safe(format(reverse(modal, kwargs={'slug': slug})))


@register.simple_tag
def show_modal(modal, *args, **kwargs):
    return mark_safe(show_modal_helper(modal, *args, **kwargs))


@register.simple_tag
def post_data(modal, modal_type,  data, *args, **kwargs):
    return mark_safe(post_data_tag(modal, modal_type, data, *args, **kwargs))


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
