import json
from base64 import urlsafe_b64encode
from ajax_helpers.templatetags.ajax_helpers import button_javascript
from django.urls import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from crispy_forms.layout import HTML, Div
from django.utils.safestring import mark_safe


DUMMY_SLUG = 'DUMMY-SLUG'

modal_buttons = {
    'edit': '<i class="fas fa-edit"></i>',
    'add':  '<i class="fas fa-plus-circle p-1"></i>',
    'delete': '<i class="fas fa-trash"></i>',
}

progress_bar_html = '''
    <div class="progress" style="margin-top: 5px;">
        <div id='file_progress_bar{}' class="progress-bar{}" role="progressbar" aria-valuenow="0" 
            aria-valuemin="0" aria-valuemax="100" style="width: 0%">
        </div>
    </div>
'''


def progress_bar(progress_id=None, css=''):
    if progress_id is not None:
        progress_id = '_' + str(progress_id)
    else:
        progress_id = ''
    if css:
        css = ' ' + css
    return progress_bar_html.format(progress_id, css)


def make_slug(*args, make_pk=False):
    slug = ''.join([str(a) for a in args])
    if make_pk and '-' not in slug:
        slug = 'pk-' + slug
    return slug


def show_modal(modal_name, *args, base64=False, datatable=False, href=False, button=None,
               button_classes='btn btn-primary mx-1', row=False, font_awesome=None):
    try:
        javascript = f"django_modal.show_modal('{reverse(modal_name, args=[DUMMY_SLUG])}')"
    except NoReverseMatch:
        javascript = f"django_modal.show_modal('{reverse(modal_name)}')"
    if base64:
        slug = urlsafe_b64encode(json.dumps(base64).encode('utf8')).decode('ascii')
    else:
        slug = make_slug(*args)
    if datatable:
        if base64:
            slug = '%ref%'
        else:
            if slug:
                slug += '-'
            slug += 'pk-%ref%'
            if row:
                slug += '-row-%row%'
    if href:
        javascript = 'javascript:' + javascript
    if button is not None:
        button_text = modal_buttons.get(button, button)
        if font_awesome:
            button_text = f'<i class="{font_awesome}"></i> {button_text}'
        javascript = f'<a {css_classes(button_classes)} href="javascript:{javascript}">{button_text}</a>'
    if not slug:
        slug = '-'
    return javascript.replace(DUMMY_SLUG, slug)


def render_modal(template_name='django_modals/modal_base.html', **kwargs):
    if 'request' in kwargs and 'modal_url' not in kwargs:
        kwargs['modal_url'] = kwargs['request'].get_full_path()
    button_kwargs = {a: kwargs[a] for a in ['button_group_class', 'button_container_class'] if a in kwargs}
    kwargs['contents'] = mark_safe(kwargs.get('contents', '') + modal_button_group(kwargs.get('modal_buttons', None),
                                                                                   **button_kwargs))
    return render_to_string(template_name, kwargs)


def css_classes(classes):
    return f' class="{classes}"' if classes else ''


def crispy_modal_link(modal_name, text, div=False, div_classes='', button_classes=''):
    link = HTML(show_modal(modal_name, button=text, button_classes=button_classes))
    if div:
        link = Div(link, css_class=div_classes)
    return link


def modal_button(title, commands, css_class='btn-primary'):
    if type(commands) == str:
        params = [{'function': commands}]
    elif type(commands) == dict:
        params = [commands]
    else:
        params = commands
    return mark_safe(f'''<button onclick='django_modal.process_commands_lock({json.dumps(params)})' 
            class="btn {css_class}">{title}</button>''')


def modal_button_method(title, method_name, css_class='btn-primary', **kwargs):
    return modal_button(title, dict(function='post_modal', button=dict(button=method_name, **kwargs)), css_class)


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


def reverse_modal(modal_name, slug='-', base64=None):
    if base64:
        slug = urlsafe_b64encode(json.dumps(base64).encode('utf8')).decode('ascii')
    try:
        return reverse(modal_name, args=[slug])
    except NoReverseMatch:
        if slug == '-':
            return reverse(modal_name)
        else:
            raise NoReverseMatch


def ajax_modal_redirect(modal_name, slug='-', base64=None):
    return [{'function': 'close'}, {'function': 'show_modal', 'modal': reverse_modal(modal_name, slug=slug,
                                                                                     base64=base64)}]


def ajax_modal_replace(request, modal_name=None, modal_class=None, slug='-', ajax_function='overwrite_modal', **kwargs):
    request.method = 'get'
    if modal_class:
        view_class = modal_class
    else:
        request.path = reverse_modal(modal_name, slug)
        view_class = resolve(request.path).func.view_class
    return {'function': ajax_function, 'html': view_class.as_view()(request, slug=slug, **kwargs).rendered_content}
