from urllib import parse
from django.core.exceptions import ValidationError
from django.forms.fields import CharField, MultipleChoiceField, ChoiceField

from django_datatables.widgets import DataTableReorderWidget, DataTableWidget
from django_datatables.datatables import DatatableView

from django_modals.helper import show_modal
from django_modals.widgets.colour_picker import ColourPickerWidget
from django_modals.widgets.select2 import Select2, Select2Multiple, MultipleChoiceFieldAddValues
from django_modals.widgets.widgets import Toggle, TinyMCE
from django_modals.widgets.jquery_datepicker import DatePicker

from show_src_code.modals import ModelFormModal

from modal_examples.models import Company, Tags, Note, Person
from .views import MainMenu
from ..models import CompanyColour


class WidgetExamples(MainMenu, DatatableView):

    template_name = 'example_views/widgets.html'

    def setup_menu(self):
        super().setup_menu()

        self.add_menu('select2', 'buttons', ).add_items(

        )
        company = Company.objects.first()
        tag = Tags.objects.first()
        self.menus['select2'].add_items(
            (f'tags_company,pk-{tag.id}', 'Many to Many'),
            (f'tags_company_add,pk-{tag.id}', 'Many to Many ADD VALUES'),
            (f'widgets_company,pk-{company.id}', 'Reverse Many to Many'),
            (f'company_tags_add,pk-{company.id}', 'Reverse Many to Many ADD VALUES'),
            )
        self.add_menu('ajax', 'buttons', ).add_items(
            (f'ajax_widgets_company,pk-{tag.id}', 'AJAX'),
            (f'people_ajax,-', 'PEOPLE AJAX'),
            (f'people_ajax,57', 'EDIT PEOPLE AJAX'),
            (f'ajax_html_template,-', 'HTML Template'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag_id'] = Tags.objects.first().id
        context['company_id'] = Company.objects.first().id
        return context


class Select2PersonCompanyForm(ModelFormModal):
    model = Person
    form_fields = ['title', 'company', 'first_name']
    widgets = {'company': Select2, 'title': Select2}


class DatatableWidgetExample(ModelFormModal):
    model = Tags
    form_fields = ['company']
    widgets = {'company': DataTableWidget(model=Company, fields=['.id', 'name'])}


class DatatableWidgetReverseExample(ModelFormModal):
    model = Company
    form_fields = []

    def form_setup(self, form, *_args, **_kwargs):
        form.fields['tags'] = MultipleChoiceField(
            choices=Tags.objects.values_list('id', 'tag'),
            widget=DataTableWidget(model=Tags, fields=['id', 'tag']),
            initial=list(self.object.tags_set.values_list('id', flat=True))
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags_set.set(form.cleaned_data['tags'])
        return response


class DatatableReorderWidgetExample(ModelFormModal):
    model = Company
    form_fields = []
    ajax_commands = ['datatable', 'button']

    def form_setup(self, form, *_args, **_kwargs):
        form.fields['modules'] = CharField(
            widget=DataTableReorderWidget(
                model=self.model,
                fields=['_.index', '.id', 'name'],
                order_field='importance',
            ))

    def datatable_sort(self, **kwargs):
        current_sort = dict(self.model.objects.values_list('id', 'importance'))
        for s in kwargs['sort']:
            if current_sort[s[1]] != s[0]:
                o = self.model.objects.get(id=s[1])
                o.importance = s[0]
                o.save()
        return self.command_response('')


class AjaxTagsCompanyForm(ModelFormModal):
    model = Tags
    form_fields = ['tag', 'company']
    widgets = {'company': Select2Multiple(attrs={'ajax': True,
                                                 'html_template': """function(text) {return "<span>" + text.id + "</span>";}""",
                                                 'html_result_template': """function(text) {return "<span>" + text.text + "</span>";}""",
                                                 })}

    def select2_company(self, **kwargs):
        return self.select2_ajax_search(filter_field='name', **kwargs)


class AjaxTemplateForm(ModelFormModal):
    model = Tags
    form_fields = ['tag',
                   'company']
    widgets = {'company': Select2Multiple(
        attrs={'ajax': True,
               'html_template': """function(text) {return "<span>" + text.text + "</span>";}""",
               'html_result_template': """function(text) {return "<span>" +  text.id + ": " +text.text + "</span>";}""",
               })}

    def select2_company(self, **kwargs):
        return self.select2_ajax_search(filter_field='name', **kwargs)

class PeopleField(ChoiceField):

    modal_name = 'company_modal'
    new_marker = 'new:'

    def __init__(self, field=None, test=None, ajax=True, **kwargs):
        self.model = None
        self.ajax = ajax
        self.widget = Select2(attrs={'ajax': self.ajax, 'tags': True})
        if test:
            self.test = test
        super().__init__(**kwargs)
        if field:
            self.field_setup(field)

    def field_setup(self, field):
        self.model = field.related_model
        if not self.ajax:
            self.widget.select_data = []
            for value in self.model.objects.all():
                self.widget.select_data.append({
                    'id': value.id,
                    'text': parse.quote(self.select_str(value), safe='~@#$&()*!+=:;,.?/')
                })

    def prepare_value(self, value):
        if not value:
            self.choices = [('', '-')]
            return
        self.choices = [(value, self.select_str(self.model.objects.get(pk=value)))]
        return super().prepare_value(value)

    @staticmethod
    def select2_button(text, onclick, css_class):
        return (f'<button onmousedown="arguments[0].stopPropagation()" '
                f'onclick="arguments[0].preventDefault();{onclick}"'
                f' class="btn btn-sm {css_class}">{text}</button>')

    @classmethod
    def select_str(cls, selected):
        return selected.name + cls.select2_button("EDIT", show_modal(cls.modal_name, selected.id), "btn-primary")

    def clean(self, value):
        if value:
            object_value = self.model.objects.filter(pk=value).first()
            if not object_value:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': value},)
            return object_value

    def widget_attrs(self, widget):
        return {'new_marker': self.new_marker}


class AjaxPersonCompanyForm(ModelFormModal):
    model = Person
    form_fields = ['company', 'first_name']
    field_classes = {'company': PeopleField(test=1)}

    def select2_company(self, **kwargs):
        return self.select2_ajax_search(**kwargs, filter_field='name')


class NoteForm(ModelFormModal):
    model = Note

    form_fields = ['company', 'date', 'notes']
    widgets = {'company': Select2, 'date': DatePicker, 'notes': TinyMCE}


class ToggleForm(ModelFormModal):
    model = Company
    form_fields = ['name', 'active']
    widgets = {'active': Toggle(attrs={'data-on': 'ACTIVE', 'data-off': 'INACTIVE'})}


class ModalCompanyForm(ModelFormModal):

    model = Company
    form_fields = []

    def form_setup(self, form, *_args, **_kwargs):
        form.fields['tags'] = MultipleChoiceField(
            choices=Tags.objects.values_list('id', 'tag'),
            widget=Select2Multiple,
            initial=list(self.object.tags_set.values_list('id', flat=True))
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.tags_set.set(form.cleaned_data['tags'])
        return response


class ModalCompanyFormAdd(ModelFormModal):

    model = Company
    form_fields = []

    def form_setup(self, form, *_args, **_kwargs):
        form.fields['tags'] = MultipleChoiceFieldAddValues(
            choices=Tags.objects.values_list('id', 'tag'),
            initial=list(self.object.tags_set.values_list('id', flat=True))
        )

    def form_valid(self, form):
        for t in form.cleaned_data['tags']['new']:
            new_tag = Tags.objects.create(tag=t)
            form.cleaned_data['tags']['existing'].append(new_tag.id)
        response = super().form_valid(form)
        self.object.tags_set.set(form.cleaned_data['tags']['existing'])
        return response


class TagsCompanyForm(ModelFormModal):
    model = Tags
    form_fields = ['tag', 'company']
    widgets = {'company': Select2Multiple()}


class TagsCompanyFormAddValues(ModelFormModal):
    model = Tags
    form_fields = ['tag', 'company']

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['company'] = MultipleChoiceFieldAddValues(choices=Company.objects.values_list('id', 'name'))

    def get_initial(self):
        initial = super().get_initial()
        initial['company'] = list(self.object.company.values_list('id', flat=True))
        return initial

    def form_valid(self, form):
        for c in form.cleaned_data['company']['new']:
            new_company = Company.objects.create(name=c)
            form.cleaned_data['company']['existing'].append(new_company.id)
        form.cleaned_data['company'] = form.cleaned_data['company']['existing']
        response = super().form_valid(form)
        return response


class CompanyColourModal(ModelFormModal):
    model = CompanyColour
    form_fields = ['company', 'colour']
    widgets = {'company': Select2,
               'colour': ColourPickerWidget}
