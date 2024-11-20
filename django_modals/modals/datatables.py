import json

from django_menus.menu import MenuMixin
from django_modals.modals import TemplateModal

from django_datatables.datatables import DatatableTable


class DatatableModal(MenuMixin, TemplateModal):
    size = 'xl'
    modal_template = 'django_modals/datatables/datatable.html'
    model = None
    table_classes = None
    table_options = None
    ajax_commands = ['row', 'column', 'datatable', 'button', 'ajax']
    show_search_bar = False

    def add_table(self, **kwargs):
        table = DatatableTable(model=self.model,
                               table_options=self.table_options,
                               table_classes=self.table_classes,
                               view=self, **kwargs)
        table.ajax_data = False
        return table

    def modal_context(self):
        context = self.kwargs.get('context', {})
        table = self.add_table()
        self.setup_table(table=table)
        context['datatable'] = table
        context['menus'] = self.menus
        context['show_search_bar'] = self.show_search_bar
        context['show_pivot_table'] = len(table.js_filter_list) > 0
        return context

    def setup_table(self, table):
        pass

    @staticmethod
    def modal_button_method_javascript(method_name, **kwargs):
        params = [dict(function='post_modal', button=dict(button=method_name, **kwargs))]
        return f'django_modal.process_commands_lock({json.dumps(params)})'.replace('"', "'")
