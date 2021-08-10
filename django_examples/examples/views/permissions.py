from django.contrib.auth import login, logout
from django.contrib.auth.models import User, Permission
from django.urls import reverse, resolve

from django_modals.processes import PERMISSION_OFF, PERMISSION_ON, PROCESS_VIEW, PROCESS_EDIT, PERMISSION_STAFF, \
    PERMISSION_AUTHENTICATED, user_has_perm
from django_modals.widgets.select2 import Select2Multiple

from examples.models import Company
from show_src_code.modals import ModelFormModal
from .views import MainMenuTemplateView


class PermissionExamples(MainMenuTemplateView):
    template_name = 'example_views/permissions.html'

    def crud_menu(self, url_name, menu_name, company_id):
        self.add_menu(menu_name, 'button_menu.html', ).add_items(
            (f'{url_name},-', 'Create'),
            (f'{url_name},pk-{company_id}', 'Edit'),
            (f'{url_name},pk-{company_id}-modal-viewedit', 'View'),
        )
        view_class = resolve(reverse(url_name, args=['-'])).func.view_class
        button_text = None
        if user_has_perm(view_class, self.request.user, PROCESS_EDIT):
            button_text = '<i class="fas fa-pen"></i> Edit'
        elif user_has_perm(view_class, self.request.user, PROCESS_VIEW):
            button_text = '<i class="fas fa-search"></i> View'
        if button_text:
            self.menus[menu_name].add_items((f'{url_name},pk-{company_id}', button_text,
                                             {'css_classes': ['btn-success']}),)

    def button_signin(self, **_kwargs):
        user = User.objects.get_or_create(username='permission_test_user')[0]
        user.save()
        login(self.request, user)
        return self.command_response('reload')

    def button_logout(self, **_kwargs):
        logout(self.request)
        return self.command_response('reload')

    def button_super_user(self, **_kwargs):
        user = User.objects.filter(is_superuser=True).first()
        login(self.request, user)
        return self.command_response('reload')

    def button_perm(self, **kwargs):
        print(kwargs)
        return self.command_response('reload')

    def setup_menu(self):
        super().setup_menu()

        company = Company.objects.first()
        self.crud_menu('perms_default', 'default', company.id)
        self.crud_menu('perms_delete', 'delete', company.id)

        self.crud_menu('perms_auth', 'auth', company.id)

        self.crud_menu('perms_on', 'perms', company.id)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['test_user'] = User.objects.filter(username='permission_test_user').first()

        return context


class DefaultCompany(ModelFormModal):

    model = Company
    form_fields = ['name']


class DeleteCompany(ModelFormModal):

    model = Company
    form_fields = ['name']
    permission_delete = PERMISSION_OFF


class CompanyPermissions(ModelFormModal):

    model = Company
    form_fields = ['name']

    permission_delete = PERMISSION_ON
    permission_edit = PERMISSION_ON
    permission_view = PERMISSION_ON
    permission_create = PERMISSION_ON


class AuthenticatedStaffPermissions(ModelFormModal):

    model = Company
    form_fields = ['name']

    permission_delete = PERMISSION_STAFF
    permission_edit = PERMISSION_AUTHENTICATED
    permission_view = PERMISSION_AUTHENTICATED
    permission_create = PERMISSION_ON


class PermUser(ModelFormModal):
    model = User
    form_fields = ['user_permissions', 'is_staff']
    widgets = {'user_permissions': Select2Multiple}

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['user_permissions'].queryset = Permission.objects.filter(name__icontains='company')
