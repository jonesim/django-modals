import json
from django.urls import reverse
from django.template.loader import render_to_string
from crispy_forms.layout import HTML, Div
from django.utils.safestring import mark_safe
from django.shortcuts import render

modal_buttons = {
    'edit': '<i class="fas fa-edit"></i>',
    'add':  '<i class="fas fa-plus-circle p-1"></i>',
    'delete': '<i class="fas fa-trash"></i>',
}


def make_slug(*args, datatable=False):

    str_args = [str(a) for a in args]
    slug = ''.join(str_args)
    if slug == '' and datatable:
        slug = '-ref-'
    elif slug == '':
        slug = '-'
    elif datatable:
        slug += '-ref-'
    return slug


def show_modal(modal_name, modal_type, *args, **kwargs):
    slug = make_slug(*args)
    javascript = f"django_modal.show_modal('{reverse(modal_name, kwargs={'slug': slug})}')"

    if modal_type == 'datatable':
        no_search = kwargs.get('no_search', True)
        if slug == '-':
            remove_chars = -4
        else:
            remove_chars = -3
        options = {
            'javascript': f"{javascript[:remove_chars]}%ref%/')",
            'colRef': kwargs.get('col_ref', 'id'),
            'nonullref': kwargs.get('nonullref', True)
        }
        if kwargs.get('row'):
            options['javascript'] = f"{javascript[:remove_chars]}pk-%ref%-row-%row%/')"
        if not no_search:
            options['text'] = ''
        else:
            options['no-col-search'] = True
        return options
    elif modal_type == 'datatable2':
        if slug == '-':
            remove_chars = -4
        else:
            remove_chars = -3
        if kwargs.get('row'):
            return f"{javascript[:remove_chars]}pk-%ref%-row-%row%/')"
        else:
            return f'{javascript[:remove_chars]}%ref%/\')'
    elif modal_type == 'href':
        return f"javascript:{javascript}"
    elif modal_type == 'javascript':
        return javascript

    elif modal_type in modal_buttons:
        name = kwargs.get('name', '')
        if name == "":
            name = modal_buttons[modal_type]
        css_class = kwargs.get('css_class', 'mx-1')
        return f'<a title="Edit" class="{css_class}" href="javascript:{javascript}">{name}</a>'


def render_modal(template_name='django_modals/modal_base.html', **kwargs):
    if 'request' in kwargs and 'modal_url' not in kwargs:
        kwargs['modal_url'] = kwargs['request'].path
    button_kwargs = {a: kwargs[a] for a in ['button_group_class', 'button_container_class'] if a in kwargs}
    kwargs['contents'] = mark_safe(kwargs.get('contents') + modal_button_group(kwargs.get('modal_buttons'),
                                                                               **button_kwargs))
    return render_to_string(template_name, kwargs)


def css_classes(classes):
    return f' class="{classes}"' if classes else ''


def crispy_modal_link(modal_name, text, div=False, div_classes='', button_classes=''):
    link = HTML(f'''<a{css_classes(button_classes)} href="{show_modal(modal_name, "href")}">{text}</a>''')
    if div:
        link = Div(link, css_class=div_classes)
    return link


def button_javascript(button_name, url_name=None, url_args=None, **kwargs):
    json_data = {'data': dict(button=button_name, **kwargs)}
    if url_name:
        if url_args is None:
            url_args = ['-']
        json_data['url'] = reverse(url_name, args=url_args)
    return f'ajax_helpers.post_json({json.dumps(json_data)})'


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
    return f'''<button onclick='django_modal.process_commands_lock({json.dumps(params)})' 
            class="btn {css_class}">{title}</button>'''


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
