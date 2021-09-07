from django import forms
from django.forms.fields import CharField, ChoiceField, BooleanField
from django_modals.forms import CrispyForm
from django_modals.fields import FieldEx

from crispy_forms.layout import HTML
from django_modals.widgets.widgets import Toggle
from .views import MainMenuTemplateView
from show_src_code.modals import FormModal


class AdaptiveView(MainMenuTemplateView):

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('adaptive_modal', 'Adaptive Modal'),
            ('adaptive_modal_boolean', 'Adaptive Modal Boolean'),
            ('adaptive_modal_select', 'Adaptive Select'),
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

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        form.add_trigger('select', 'onchange', [
            {'selector': '#div_id_if_one', 'values': {'1': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_two', 'values': {'2': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_three', 'values': {'3': 'show'}, 'default': 'hide'},
            {'selector': '#div_id_if_one,#div_id_if_two,#div_id_if_three', 'values': {'all': 'show'}},
            {'selector': '#div_id_if_one', 'values': {'all': 'clear'}},
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

