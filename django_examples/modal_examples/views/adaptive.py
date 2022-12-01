from django import forms
from django.forms.fields import CharField, ChoiceField, BooleanField
from django_modals.forms import CrispyForm
from django_modals.fields import FieldEx

from crispy_forms.layout import HTML
from show_src_code.modals import ModelFormModal

from django_modals.widgets.select2 import Select2
from django_modals.widgets.widgets import Toggle
from .views import MainMenuTemplateView
from show_src_code.modals import FormModal

from ..models import CompanyColour


class AdaptiveView(MainMenuTemplateView):

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('adaptive_modal', 'Adaptive Modal'),
            ('adaptive_modal_boolean', 'Adaptive Modal Boolean'),
            ('adaptive_modal_select', 'Adaptive Select'),
            ('adaptive_label_change_modal', 'Label Change'),
            ('adaptive_ajax_modal,-', 'Adaptive Ajax'),
        )


class TestForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    select = ChoiceField(choices=(('1', 'one'), ('2', 'two'), ('3', 'three'), ('all', 'all')), widget=forms.RadioSelect)
    if_one = CharField(label='Field for 1', required=True)
    if_two = CharField(label='Field for 2', required=False)
    if_three = CharField(label='Field for 3', required=False)


class AdaptiveModal(FormModal):
    form_class = TestForm

    def button_test_X(self, **kwargs):
        return self.command_response('')

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.add_trigger('select', 'onchange', [
            #{'selector': '#div_id_if_one', 'values': {'1': 'show'}, 'default': 'hide'},
            #{'selector': '#div_id_if_two', 'values': {'2': 'show'}, 'default': 'hide'},
            #{'selector': '#div_id_if_three', 'values': {'3': 'show'}, 'default': 'hide'},
            #{'selector': '#div_id_if_one,#div_id_if_two,#div_id_if_three', 'values': {'all': 'show'}},
            #{'selector': '#div_id_if_one', 'values': {'all': 'clear'}},
            {'button': 'test_X', 'default': 'send_inputs', 'values': {}},
        ])

        # noinspection PyTypeChecker
        return [HTML('<p>Different selections show different bottom field</p>'
                     '<p>Field for 1 is cleared every time Select changes</p>')] + [FieldEx(f) for f in form.fields]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TestBooleanForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    show_extra = BooleanField(required=False, widget=Toggle)
    extra_field = CharField(required=False)


class AdaptiveBooleanModal(FormModal):
    form_class = TestBooleanForm

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.add_trigger('show_extra', 'onchange', [
            {'selector': '#div_id_extra_field', 'values': {'checked': 'show'}, 'default': 'hide'},
        ])

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        return context


class TestSelectForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    select = ChoiceField(choices=(('1', 'one'), ('2', 'two'), ('3', 'three'), ('all', 'all')))
    if_one = CharField(label='Field for 1', required=True)
    if_two = CharField(label='Field for 2', required=False)
    if_three = CharField(label='Field for 3', required=False)


class AdaptiveSelectModal(FormModal):
    form_class = TestSelectForm

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.add_trigger('select', 'onchange', [
            {'selector': '#div_id_if_one', 'values': {'1': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_two', 'values': {'2': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_three', 'values': {'3': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_one,#div_id_if_two,#div_id_if_three', 'values': {'all': 'show'}},
            {'selector': '#div_id_if_one', 'values': {'all': 'clear'}},

        ])


class LabelChangeForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    select = ChoiceField(choices=(('1', 'one'), ('2', 'two'), ('3', 'three'), ('all', 'all')))
    test_field = CharField(required=True)


class LabelChangeModal(FormModal):
    form_class = LabelChangeForm

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.add_trigger('select', 'onchange', [
            {'selector': 'label[for=id_test_field]',
             'values': {'1': ('html', 'one'),
                        '2': ('html', 'two'),
                        '3': ('html', '3')}, 'default': ('html', 'na')},
        ])


class AdaptiveAjaxModal(ModelFormModal):
    ajax_commands = ['button', 'tooltip', 'timer', 'ajax', 'select2']
    model = CompanyColour
    form_fields = ['company']
    widgets = {'company': Select2(attrs={'selected_ajax': 'form', 'cleared_ajax': 'form'})}

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **self.kwargs)

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.fields['company_id'] = CharField(required=False)
        form.fields['company_id'].widget.attrs['disabled'] = 'disabled'

    def select2_company_selected(self, **kwargs):
        return self.command_response('set_value', selector='#id_company_id', val=f'{kwargs["company"]}')

    def select2_company_cleared(self, **kwargs):
        return self.command_response('set_value', selector='#id_company_id', val='N/A')
