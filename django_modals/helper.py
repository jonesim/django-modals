import json
from base64 import urlsafe_b64encode
from ajax_helpers.templatetags.ajax_helpers import button_javascript
from django.urls import reverse, resolve, NoReverseMatch
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from html_classes.font_awesome import font_awesome as fa_icon
from html_classes.html import HtmlA, HtmlButton, HtmlDiv


DUMMY_SLUG = 'DUMMY-SLUG'

modal_buttons = {
    'edit': fa_icon('fas fa-edit'),
    'add':  fa_icon('fas fa-plus-circle p-1'),
    'delete': fa_icon('fas fa-trash'),
}


def base64_json(slug_dict):
    return urlsafe_b64encode(json.dumps(slug_dict).encode("utf8")).decode("ascii")


def progress_bar(progress_id=None, css=''):
    progress_id = '_' + str(progress_id) if progress_id is not None else ''
    bar = HtmlDiv(css_classes=f'progress-bar{" " + css if css else ""}', id=f'file_progress_bar{progress_id}',
                  role='progressbar', aria_valuenow='0', aria_valuemin='0', aria_valuemax='100',
                  raw_attributes={'style': 'width: 0%'})
    return HtmlDiv(bar, css_classes='progress', raw_attributes={'style': 'margin-top: 5px;'}).render()


def make_slug(*args, make_pk=False):
    slug = ''.join([str(a) for a in args])
    if make_pk and '-' not in slug:
        slug = 'pk-' + slug
    return slug


def attr(attributes, tooltip):
    attributes = {} if attributes is None else attributes
    if tooltip:
        attributes.update({'title': tooltip, 'data-tooltip': 'tooltip', 'data-placement': 'top'})
    return attributes


def show_modal(modal_name, *args, base64=False, datatable=False, href=False, button=None,
               button_classes='btn btn-primary mx-1', row=False, font_awesome=None, attributes=None, tooltip=None):
    try:
        javascript = f"django_modal.show_modal('{reverse(modal_name, args=[DUMMY_SLUG])}')"
    except NoReverseMatch:
        javascript = f"django_modal.show_modal('{reverse(modal_name)}')"
    if base64:
        slug = base64_json(base64)
    else:
        slug = make_slug(*args)
    if datatable:
        if base64:
            slug = '%ref%'
        else:
            if slug == '-':
                slug = ''
            elif slug:
                slug += '-'
            slug += 'pk-%ref%'
            if row:
                slug += '-row-%row%'
    if href:
        javascript = 'javascript:' + javascript
    if button is not None:
        button_text = modal_buttons.get(button, button)
        attributes = attr(attributes, tooltip)
        contents = f'{fa_icon(font_awesome)} {button_text}' if font_awesome else button_text
        javascript = HtmlA(contents, css_classes=button_classes or None,
                           href=f'javascript:{javascript}', **attributes).render()
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
    from .layout import HTML, Div
    link = HTML(show_modal(modal_name, button=text, button_classes=button_classes))
    if div:
        link = Div(link, css_class=div_classes)
    return link


def modal_button(title, commands, css_class='btn-primary', font_awesome=None, tooltip=None):
    if type(commands) == str:
        params = [{'function': commands}]
    elif type(commands) == dict:
        params = [commands]
    else:
        params = commands

    if font_awesome:
        title = f'{fa_icon(font_awesome)} {title}'
    attributes = {'onclick': f'django_modal.process_commands_lock({json.dumps(params)})', 'type': 'button'}
    if tooltip:
        attributes.update({'data-tooltip': 'tooltip', 'title': tooltip})
    return HtmlButton(title, css_classes=f'btn {css_class}', single_quote=True, **attributes).render()


def modal_button_method(title, method_name, css_class='btn-primary', font_awesome=None, **kwargs):
    return modal_button(title, dict(function='post_modal', button=dict(button=method_name, **kwargs)),
                        css_class, font_awesome)


def modal_button_group(buttons=None, button_container_class=None, button_group_class='btn-group'):

    group_class = f'form-buttons{" " + button_container_class if button_container_class else ""}'
    if type(buttons) == str:
        inner = buttons
    elif buttons:
        inner = ''.join(str(b) for b in buttons)
    else:
        return ''
    return HtmlDiv(HtmlDiv(inner, css_classes=button_group_class), css_classes=group_class).render()


def modal_delete_javascript(url_name, pk):
    return mark_safe(button_javascript('delete', url_name=url_name, url_args=[pk]).replace('"', "'"))


def reverse_modal(modal_name, slug='-', base64=None):
    if base64:
        slug = base64_json(base64)
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
        request.path = reverse_modal(modal_name, slug, base64=kwargs.get('base64'))
        view_class = resolve(request.path).func.view_class
    return {'function': ajax_function, 'html': view_class.as_view()(request, slug=slug, **kwargs).rendered_content}
