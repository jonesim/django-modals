import json
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.forms.fields import CharField

from django_datatables.columns import ColumnBase, ManyToManyColumn
from django_datatables.datatables import DatatableView
from django_datatables.helpers import row_button

from show_src_code.modals import ModelFormModal, BaseSourceCodeModal

from django_modals.widgets.select2 import Select2Multiple
from django_modals.datatables import ModalLink, DeleteColumn, EditColumn
from django_modals.processes import PERMISSION_ON

from .views import MainMenu


class ModalUser(ModelFormModal):
    model = User
    form_fields = ['username', 'groups', 'user_permissions']
    widgets = {'groups': Select2Multiple, 'user_permissions': Select2Multiple}
    permission_delete = PERMISSION_ON

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['password'] = CharField(required=False)
        from django.contrib.auth.models import Permission
        form.fields['user_permissions'].queryset = Permission.objects.filter(name__icontains='company')

    def form_valid(self, form):
        form.save()
        if 'password' in form.cleaned_data:
            self.object.set_password(form.cleaned_data['password'])
        self.object.is_staff = True
        self.object.save()
        return self.command_response('close')


class ModalGroup(ModelFormModal):
    model = Group
    form_fields = ['name', ('permissions', {'widget': Select2Multiple})]


class UserExamples(MainMenu, DatatableView):

    template_name = 'example_views/users.html'
    model = User
    ajax_commands = ['row']

    def setup_menu(self):
        super().setup_menu()

        self.add_menu('modals', 'button_menu.html', ).add_items(
            ('user_modal,-', 'User'),
            ('group_modal,-', 'Group'),
        )

    def add_tables(self):
        self.add_table('user_table', model=User)
        self.add_table('group_table', model=Group)

    @staticmethod
    def setup_user_table(table):
        table.add_columns(
            'id',
            'username',
            ManyToManyColumn(column_name='Groups', field='groups__name', model=User),
            ModalLink(field=['id', 'username'], modal_name='user_modal'),
            EditColumn('user_modal'),
            DeleteColumn('user_modal'),
            ColumnBase(column_name='BasicButton', title='', no_col_search=True,
                       render=[row_button('select_user', 'Login',)]),
        )
        table.ajax_data = False

    @staticmethod
    def setup_group_table(table):
        table.add_columns('id', 'name', EditColumn('group_modal'))

    def row_select_user(self, **kwargs):
        row = json.loads(kwargs['row_data'])
        user = User.objects.get(pk=row[0])
        login(self.request, user)
        return self.command_response('reload')


class SourceCodeModal(BaseSourceCodeModal):
    code = {
        'user_view': UserExamples,
    }
