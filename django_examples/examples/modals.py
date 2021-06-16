import datetime
from django.urls import reverse
from django.forms.fields import CharField
from django.template.loader import render_to_string
from crispy_forms.layout import Field, HTML
from django_modals.forms import ModelCrispyForm, CrispyForm
from django_modals.view_mixins import BootstrapModelModalMixin, BootstrapModalMixinBase, BootstrapModalMixin, \
    BaseModal, MultiForm, MultiFormView

from django_modals.widgets.select2 import Select2
from .models import Company, Person


class ModalCompanyForm(BootstrapModelModalMixin):

    model = Company
    modal_title = ['New', 'Edit']
    form_fields = ['name']


class ModalCompanyFormExtraField(BootstrapModelModalMixin):

    model = Company
    modal_title = ['New', 'Edit']
    form_fields = ['name']
    form_delete = True

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['extra'] = CharField()


class ModalCompanyFormPeople(BootstrapModelModalMixin):
    model = Company
    modal_title = ['New', 'Edit']
    form_fields = ['name']
    form_delete = True

    def form_setup(self, form, *_args, **_kwargs):
        if self.object.id:
            form.modal_title = (f'Edit Company  <a href="{reverse("company", args=(self.object.id,))}">'
                                f'{self.object.name}</a>')
        return Field(*form.Meta.fields), HTML(render_to_string('people.html', {'company': form.instance}))

    def form_valid(self, form):
        if not self.object.id:
            form.save()
            self.request.path = reverse('company_people_modal', kwargs={'slug': self.object.id})
            self.add_command('overwrite_modal', html=self.get(self.request, pk=self.object.id).rendered_content)
        return super().form_valid(form)


class ModalPersonForm(BootstrapModelModalMixin):

    model = Person
    modal_title = ['New Person', 'Edit Person']
    form_fields = ['title', 'company', 'first_name', 'surname']
    form_delete = True
    widgets = {'title': Select2, 'company': Select2}

    def form_valid(self, form):
        # Haven't used auto_now so setting manually
        self.object.date_entered = datetime.date.today()
        return super().form_valid(form)

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['company'].queryset = Company.objects.filter(id__gt=1)


class ModalPersonNoCompanyForm(BootstrapModelModalMixin):

    model = Person
    modal_title = ['New Person', 'Edit Person']
    form_fields = ['title', 'first_name', 'surname']
    form_delete = True
    widgets = {'title': Select2, 'company': Select2}

    def form_valid(self, form):
        # Haven't used auto_now so setting manually
        self.object.date_entered = datetime.date.today()
        return super().form_valid(form)


class CompanyForm(ModelCrispyForm):

    class Meta:
        model = Company
        fields = ['name']
        modal_title = ['Add Company', 'Edit Company']
        delete = True


class ModalCompanySeparateForm(BootstrapModelModalMixin):
    form_class = CompanyForm


class ModalCompanyPerson(MultiFormView):

    modal_title = 'Multi form example'
    forms = [
        MultiForm(Company, ['name']),
        MultiForm(Person, ['title', 'first_name', 'surname']),
    ]

    def forms_valid(self, forms):
        company = forms['CompanyForm'].save()
        forms['PersonForm'].instance.company = company
        forms['PersonForm'].instance.date_entered = datetime.date.today()
        forms['PersonForm'].save()
        return self.command_response('reload')


class HelloModal(BootstrapModalMixinBase):
    template_name = 'modal/ok.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'hello'
        return context


class ModalButtons(BaseModal):
    template_name = 'modal_buttons.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'hello'
        return context

    def button_yes(self, **_kwargs):
        self.add_command('message', text='You pressed YES')
        return self.command_response('close')

    def button_change(self, **_kwargs):
        return self.command_response(
            'overwrite_modal',
            html=render_to_string('modal/confirm.html', {'request': self.request, 'css': 'modal', 'size': 'md',
                                                         'button_function': 'yes',
                                                         'message': 'You pressed the button'})
        )


class TestForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    def post_init(self, *args, **kwargs):
        self.fields['name'] = CharField()
        self.fields['field_2'] = CharField()


class FormModal(BootstrapModalMixin):
    form_class = TestForm
