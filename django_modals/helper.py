import json
from django.urls import reverse

modal_buttons = {
    'edit': '<i class="fas fa-edit"></i>',
    'add':  '<i class="fas fa-plus-circle p-1"></i>'
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
    javascript = f"modal.show_modal('{reverse(modal_name, kwargs={'slug': slug})}')"

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


def post_data(modal_name, modal_type, data, *args, **kwargs):
    if modal_type == 'datatable' or kwargs.get('datatable'):
        slug = make_slug(*args, datatable=True)
    else:
        slug = make_slug(*args)
    if modal_type == 'raw' or modal_type == 'raw-href':
        json_data = data
    else:
        json_data = json.dumps(data).replace('"', "'")
    modal_url = reverse(modal_name, kwargs={'slug': slug})
    javascript = f"ajax_helpers.send_form('{modal_url}', null, {json_data})"
    if modal_type == 'datatable' or kwargs.get('datatable'):
        javascript = javascript.replace('-ref-', '%ref%')
    if modal_type == 'javascript' or modal_type == 'raw':
        return javascript
    elif modal_type == 'href' or modal_type == 'raw-href':
        return f"javascript:{javascript}"
    elif modal_type == 'datatable':

        no_search = kwargs.get('no_search', True)
        options = {
            'javascript': javascript,
            'colRef': kwargs.get('col_ref', 'id'),
            'nonullref': kwargs.get('nonullref', True)
        }
        if not no_search:
            options['text'] = ''
        else:
            options['no-col-search'] = True
        return options


def post_data_tag(modal_name, modal_type, *args, **kwargs):
    return post_data(modal_name, modal_type, *args, **kwargs)
