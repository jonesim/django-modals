import datetime
import inspect
from django import forms
from django.urls import reverse
from django.forms.fields import CharField, ChoiceField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.html import escape

from crispy_forms.layout import Field, HTML, Div

import django_modals.view_mixins as view_mixins
from django_modals.forms import ModelCrispyForm, CrispyForm
from django_modals.fields import multi_row, MultiField, FieldNoLabel, PrependedTextOptions
from django_modals.widgets.select2 import Select2

from .models import Company, Person


class CodeMixin:

    def html_code(self, object):
        result = f'''<div class="bg-secondary text-light">{inspect.getsourcefile(object)}<span class="pl-4">
            Line: <b>{inspect.getsourcelines(object)[1]}</b></span></div>'''
        return result + f'<pre><code class="python-html">{escape(inspect.getsource(object))}</code></pre>'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['footer'] = mark_safe('''<div class="p-1" style="text-align:right;background-color:#efefef">
            <button class='btn btn-sm btn-outline-secondary' onclick='django_modal.send_inputs({"button": "code"})'>
            <i class="fab fa-python"></i> Source Code</button></div>''')
        return context

    def button_code(self, **_kwargs):
        code = ''
        try:
            if hasattr(self, 'form_class'):
                code = self.html_code(self.form_class)
        except OSError:
            pass
        code += self.html_code(self.__class__)

        return self.command_response(
            'modal_html', html=render_to_string('modal/ok.html', dict(
                request=self.request, css='modal', size='xl',
                message=mark_safe(code),
                script=mark_safe('hljs.highlightAll();'),
                header='Source Code',
            ))
        )


class BootstrapModalMixin(CodeMixin, view_mixins.BootstrapModalMixin):
    pass


class BootstrapModelModalMixin(CodeMixin, view_mixins.BootstrapModelModalMixin):
    pass


class MultiFormView(CodeMixin, view_mixins.MultiFormView):
    pass


class BaseModal(CodeMixin, view_mixins.BaseModal):
    pass


class PersonForm(ModelCrispyForm):
    class Meta:
        model = Person
        fields = ['first_name', 'surname', 'title']

    def post_init(self, *args, **kwargs):
        from django_modals.fields import ChoiceFieldExtra
        from .models import Person
        # self.fields['title'] = ChoiceFieldExtra()
        self.fields['title'] = ChoiceFieldExtra(widget=Select2(attrs={'tags': True}),
                                                choices=Person.title_choices)
        return (
            Field('title'),
            self.row(
                self.label('ABCx'), self.field_section(FieldNoLabel('first_name', onkeyup='test(this)'))),
            Div(PrependedTextOptions('surname', 'k', input_size='input-group-sm', label_class='d-none'), id='xx')
                )
        # return (FieldBootStrap('surname', wrapper_class='m-4'),)
        # return (MultiField('first_name'), FieldNoLabel('surname', width=400),)
        # return (Field('first_name',  label_class='p-4', field_class='bg-primary'), FieldBootStrap('surname',
        # label_class='p-4', field_class='bg-primary'), FieldBootStrap('title'))
        # return (self.label('ABC'), multi_row('x', (MultiField('surname'),
        # MultiField('first_name', label_class='d-none'))))
        # return (FieldBootStrap('first_name', 'surname', css_class='form-control-sm',
        # field_class='form-group-sm', group_class='d-flex',
        #                  label_class='form-control-sm'))


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
        form.read_only = True
        form.fields['extra'] = CharField()


class ModalCompanyFormPeople(BootstrapModelModalMixin):
    model = Company
    modal_title = ['New', 'Edit']
    form_fields = ['name']
    form_delete = True

    @property
    def delete_message(self):
        return f'Are you sure you want to delete id:{self.object.id}  {self.object.name} ?'

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
        # form.read_only = True
        form.fields['company'].queryset = Company.objects.filter(id__gt=1)


class ModalPersonNoCompanyForm(BootstrapModelModalMixin):

    model = Person
    modal_title = ['New Person', 'Edit Person', 'View Person']
    form_fields = ['title', 'first_name', 'surname']
    form_delete = True
    widgets = {'title': Select2, 'company': Select2}

    def form_valid(self, form):
        # Haven't used auto_now so setting manually
        self.object.date_entered = datetime.date.today()
        return super().form_valid(form)

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        # form.read_only = True
        pass


class CompanyForm(ModelCrispyForm):

    class Meta:
        model = Company
        fields = ['name']
        modal_title = ['Add Company', 'Edit Company']
        form_delete = True
        # no_buttons = True

    def post_init(self, *args, **kwargs):
        self.fields['name'].label = False
        return (Field('name', form_show_labels=False, wrapper_class='CC',  css_classes='CSS_CLASSES',
                      label_class='LABEL_CLASS', style='width:100px'), )


class ModalCompanySeparateForm(BootstrapModelModalMixin):
    form_class = CompanyForm


class ModalPersonSeparateForm(BootstrapModelModalMixin):
    form_class = PersonForm

    field_actions = {'first_name': {'selector': '#xx', 'values': {'': 'hide'}, 'default': 'show'},
                     'switch': {'selector': '#xx', 'values': {'checked': 'disable'}, 'default': 'enable'},
                     'choices': [
                         {'selector': '#xx', 'values': {'1': 'hide'}, 'default': 'show'},
                         {'selector': '#div2', 'values': {'1': 'hide', '2': 'hide'}, 'default': 'show'}
                     ]}

    # extra_context = (dict(script=mark_safe(f'modal_disable={json.dumps(field_actions)}')))

    def get_context_data(self, **kwargs):
        self.add_trigger('choices', 'onchange', [
            {'selector': '#xx', 'values': {'1': 'hide'}, 'default': 'show'},
            {'selector': '#div2', 'values': {'1': 'hide', '2': 'hide'}, 'default': 'show'}
        ])
        self.add_trigger('first_name', 'onkeyup',  {'selector': '#xx', 'values': {'': 'hide'}, 'default': 'show'})
        self.add_trigger('switch', 'onchange', dict(selector='#xx', values={'checked': 'disable'}, default='enable'))

        context = super().get_context_data(**kwargs)
#        context['form'].helper['choices'].update_attributes(onchange='alter_form(this)')

        return context


class ModalCompanyPerson(MultiFormView):

    modal_title = 'Multi form example'
    forms = [
        view_mixins.MultiForm(Company, ['name']),
        view_mixins.MultiForm(Person, ['title', 'first_name', 'surname']),
    ]

    # @staticmethod
    # def form_setup(form, *_args, **_kwargs):
    #     form.read_only=True

    def forms_valid(self, forms):
        company = forms['CompanyForm'].save()
        forms['PersonForm'].instance.company = company
        forms['PersonForm'].instance.date_entered = datetime.date.today()
        forms['PersonForm'].save()
        return self.command_response('reload')


class HelloModal(BaseModal):
    template_name = 'modal/ok.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = 'hello'
        return context


class ModalButtons(BaseModal):
    template_name = 'modal_buttons.html'

    @property
    def extra_context(self):
        return {'message': 'hi there'}

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
        self.fields['select'] = ChoiceField(choices=(('1', 'one'), ('2', 'two'), ('3', 'three'),
                                                     ('all', 'all')), widget=forms.RadioSelect)
        self.fields['if_one'] = CharField(label='Field for 1')
        self.fields['if_two'] = CharField(label='Field for 2')
        self.fields['if_three'] = CharField(label='Field for 3')


class FormModal(BootstrapModalMixin):
    form_class = TestForm

    def get_context_data(self, **kwargs):
        self.add_trigger('select', 'onchange', [
            {'selector': '#div_id_if_one', 'values': {'1': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_two', 'values': {'2': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_three', 'values': {'3': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_one,#div_id_if_two,#div_id_if_three', 'values': {'all': 'show'}},
            {'selector': '#div_id_if_one', 'values': {'all': 'clear'}},
        ])
        context = super().get_context_data(**kwargs)
        return context
