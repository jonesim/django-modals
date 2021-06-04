from django.db.models import Count
from django_datatables.columns import ColumnBase, DatatableColumn
from django_datatables.datatables import DatatableView
from django_modals.helper import show_modal

from . import models


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

    def setup_table(self, table):

        table.add_columns(
            ('id', {'column_defs': {'width': '30px'}}),
            'name',
            'Tags',
            ColumnBase(column_name='people', field='people', annotations={'people': Count('person__id')}),
            self.EditColumn(column_name='t'),
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
