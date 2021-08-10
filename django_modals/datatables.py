from django_datatables.columns import ColumnBase
from django_datatables.helpers import render_replace

from django_modals.helper import modal_buttons, modal_delete_javascript
from .helper import show_modal


class ModalLink(ColumnBase):

    def __init__(self, *, modal_name,  field='id', row_modify=False, button_text=None, modal_args=(), css_class=None,
                 **kwargs):
        if not self.initialise(locals()):
            return
        super().__init__(**self.kwargs)
        modal_kwargs = {}
        if row_modify:
            modal_kwargs['row'] = True
        modal_call = show_modal(modal_name, *modal_args, datatable=True, href=True, **modal_kwargs)
        css_class = f' class="{css_class}"' if css_class is not None else ""
        link = f'<a href="{modal_call}"{css_class}>{{}}</a>'

        if button_text:
            self.options['render'] = [
                render_replace(column=self.column_name, html=link.format(button_text), var='%ref%'),
            ]
        else:
            self.options['render'] = [
                render_replace(column=f'{self.column_name}:0', html=link.format('%1%'), var='%ref%'),
                render_replace(column=f'{self.column_name}:1')
            ]


class EditColumn(ModalLink):
    def __init__(self, modal_name, button_text='Edit', css_class='btn btn-sm btn-primary', title='',
                 no_col_search=True, **kwargs):
        super().__init__(modal_name=modal_name, button_text=button_text, title=title, no_col_search=no_col_search,
                         css_class=css_class, **kwargs)
        self.column_defs = {
            'orderable': False,
            'className': 'dt-center'
        }


class DeleteColumn(ColumnBase):

    def __init__(self, modal_name,  field='id', button_text=None, css_class=None, no_col_search=True, title='',
                 **kwargs):
        if not self.initialise(locals()):
            return
        super().__init__(**self.kwargs)
        css_class = css_class if css_class else 'text-danger'
        button_text = button_text if button_text else modal_buttons['delete']
        self.column_defs['orderable'] = False
        self.column_defs['className'] = 'dt-center'
        self.options['render'] = [render_replace(
            var='999999',
            html=f'<a class="{css_class}" href="javascript:{modal_delete_javascript(url_name=modal_name, pk=999999)}">'
                 f'{button_text}</a>'
        )]
