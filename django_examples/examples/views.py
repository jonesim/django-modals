import json
from django.db.models import Count
from django_datatables.columns import ColumnBase, DatatableColumn
from django_datatables.datatables import DatatableView
from django_modals.helper import show_modal
from django.urls import reverse
from . import models
from django_modals.helper import modal_buttons


def button_javascript(button_name, url_name=None, url_args=None, **kwargs):
    json_data = {'data': dict(button=button_name, **kwargs)}
    if url_name:
        json_data['url'] = reverse(url_name, args=url_args)
    return f'ajax_helpers.post_json({json.dumps(json_data)})'


def delete_datatable(url_name):
    return {
        'html': f'''<button class='btn btn-sm' 
                    onclick='{button_javascript('delete', url_name=url_name, url_args=(999999,))}'>
                    {modal_buttons['delete']}
                    </button>''',
        'var': '999999',
        'column': 'id',
        'function': 'Replace'
    }


class Example1(DatatableView):
    model = models.Company
    template_name = 'table.html'

    class EditColumn(DatatableColumn):

        def col_setup(self):
            self.title = 'Edit'
            self.options['render'] = [{
                'html': (f'<a class="btn btn-sm btn-secondary" '
                                  f'href="javascript:{show_modal("company_people_modal", "datatable2")}">EDIT</a>'),
                'var': '%ref%',
                'column': 'id',
                'function': 'Replace'
            }]

    class DeleteColumn(DatatableColumn):

        def col_setup(self):
            self.title = 'Delete'
            self.options['render'] = [{
                'html': f'''<button class='btn btn-sm' onclick='{button_javascript('delete', url_name='company_people_modal', url_args=(999999,))}'>{modal_buttons['delete']}</button>''',
                'var': '999999',
                'column': 'id',
                'function': 'Replace'
            }]

    def setup_table(self, table):

        table.add_columns(
            ('id', {'column_defs': {'width': '30px'}}),
            'name',
            'Tags',
            ColumnBase(column_name='people', field='people', annotations={'people': Count('person__id')}),
            self.EditColumn(column_name='t'),
            self.DeleteColumn(column_name='tx'),
            ('del', {'calculated': True,'render': [delete_datatable('company_people_modal')]}),
        )
        table.ajax_data = False
        table.add_js_filters('tag', 'Tags')

    def add_to_context(self, **kwargs):
        return {'title': type(self).__name__, 'filter': filter}


class Example2(DatatableView):
    model = models.Person
    template_name = 'table2.html'

    def setup_table(self, table):

        table.add_columns(
            'id',
            'first_name',
            'surname',
            ('company__name', {'title': 'Company Name'}),
            'company__collink_1'
        )
        if 'pk' in self.kwargs:
            table.filter = {'company__id': self.kwargs['pk']}
        table.add_js_filters('select2', 'company__name')
        table.add_js_filters('totals', 'id')

    def add_to_context(self, **kwargs):
        context = {'description': '''
        '''}

        if 'pk' in self.kwargs:
            context['title'] = type(self).__name__ + ' ' + ' pk:' + str(self.kwargs['pk'])
        else:
            context['title'] = type(self).__name__
        return context


class CompanyView(DatatableView):
    template_name = 'table.html'

    def add_to_context(self, **kwargs):
        return {'title': type(self).__name__ + ' ' + ' pk:' + str(self.kwargs['pk'])}

    def setup_table(self, table):
        pass
