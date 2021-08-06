import json
from ajax_helpers.templatetags.ajax_helpers import button_javascript
from django.urls import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from crispy_forms.layout import HTML, Div
from django.utils.safestring import mark_safe
from django.shortcuts import render


DUMMY_SLUG = 'DUMMY-SLUG'

modal_buttons = {
    'edit': '<i class="fas fa-edit"></i>',
    'add':  '<i class="fas fa-plus-circle p-1"></i>',
    'delete': '<i class="fas fa-trash"></i>',
}


def make_slug(*args, make_pk=False):
    slug = ''.join([str(a) for a in args])
    if make_pk and '-' not in slug:
        slug = 'pk-' + slug
    return slug


def show_modal(modal_name, *args, datatable=False, href=False, button=None, button_classes='btn btn-primary mx-1',
               row=False):
    try:
        javascript = f"django_modal.show_modal('{reverse(modal_name, args=[DUMMY_SLUG])}')"
    except NoReverseMatch:
        javascript = f"django_modal.show_modal('{reverse(modal_name)}')"
    slug = make_slug(*args)
    if datatable:
        if slug:
            slug += '-'
        slug += 'pk-%ref%'
        if row:
            slug += '-row-%row%'
    if href:
        javascript = 'javascript:' + javascript
    if button:
        button_text = modal_buttons.get(button, button)
        javascript = f'<a {css_classes(button_classes)} href="javascript:{javascript}">{button_text}</a>'
    if not slug:
        slug = '-'
    return javascript.replace(DUMMY_SLUG, slug)


def render_modal(template_name='django_modals/modal_base.html', **kwargs):
    if 'request' in kwargs and 'modal_url' not in kwargs:
        kwargs['modal_url'] = kwargs['request'].path
    button_kwargs = {a: kwargs[a] for a in ['button_group_class', 'button_container_class'] if a in kwargs}
    kwargs['contents'] = mark_safe(kwargs.get('contents', '') + modal_button_group(kwargs.get('modal_buttons', ''),
                                                                                   **button_kwargs))
    return render_to_string(template_name, kwargs)


def css_classes(classes):
    return f' class="{classes}"' if classes else ''


def crispy_modal_link(modal_name, text, div=False, div_classes='', button_classes=''):
    link = HTML(show_modal(modal_name, button=text, button_classes=button_classes))
    if div:
        link = Div(link, css_class=div_classes)
    return link


def overwrite_message(view, message, header=None):
    message_modal = render_modal('django_modals/ok.html', message=message, header=header)
    if view.request.is_ajax():
        return view.command_response('overwrite_modal', html=message_modal)
    else:
        return render(view.request, 'django_modals/blank_page_form.html', context={'form': message_modal})


def modal_button(title, commands, css_class='btn-primary'):
    if type(commands) == str:
        params = [{'function': commands}]
    elif type(commands) == dict:
        params = [commands]
    else:
        params = commands
    return mark_safe(f'''<button onclick='django_modal.process_commands_lock({json.dumps(params)})' 
            class="btn {css_class}">{title}</button>''')


def modal_button_method(title, method_name, css_class='btn-primary'):
    return modal_button(title, {'function': 'post_modal', 'button': method_name}, css_class)


def modal_button_group(buttons=None, button_container_class=None, button_group_class='btn-group'):

    group_class = f'form-buttons{" " + button_container_class if button_container_class else ""}'
    if type(buttons) == str:
        return f'<div class="{group_class}"><div class="{button_group_class}">{buttons}</div></div>'
    if buttons:
        return (f'<div class="{group_class}">'
                f'<div class="{button_group_class}">{"".join(buttons)}</div></div>')
    return ''


def modal_delete_javascript(url_name, pk):
    return mark_safe(button_javascript('delete', url_name=url_name, url_args=[pk]).replace('"', "'"))


def ajax_modal_redirect(modal_name, slug='-'):
    return [{'function': 'close'},
            {'function': 'show_modal', 'modal': reverse(modal_name, kwargs={'slug': slug})}]


def reverse_modal(modal_name, slug='-'):
    try:
        return reverse(modal_name, args=slug)
    except NoReverseMatch:
        return reverse(modal_name)


def ajax_modal_replace(request, modal_name=None, modal_class=None, slug='-', ajax_function='overwrite_modal', **kwargs):
    request.method = 'get'
    if modal_class:
        view_class = modal_class
    else:
        request.path = reverse_modal(modal_name, slug)
        view_class = resolve(request.path).func.view_class
    return {'function': ajax_function, 'html': view_class.as_view()(request, slug=slug, **kwargs).rendered_content}
