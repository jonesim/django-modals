from django import forms
from django.forms.fields import CharField, ChoiceField
from django_modals.forms import CrispyForm
from django_modals.fields import FieldEx

from crispy_forms.layout import HTML

from .views import MainMenuTemplateView
from show_src_code.modals import FormModal


class AdaptiveView(MainMenuTemplateView):

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('adaptive_modal', 'Adaptive Modal'),
        )


class TestForm(CrispyForm):

    class Meta:
        modal_title = 'Test Title'

    select = ChoiceField(choices=(('1', 'one'), ('2', 'two'), ('3', 'three'), ('all', 'all')), widget=forms.RadioSelect)
    if_one = CharField(label='Field for 1', required=False)
    if_two = CharField(label='Field for 2', required=False)
    if_three = CharField(label='Field for 3', required=False)


class AdaptiveModal(FormModal):
    form_class = TestForm

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        # noinspection PyTypeChecker
        return [HTML('<p>Different selections show different bottom field</p>'
                     '<p>Field for 1 is cleared every time Select changes</p>')] + [FieldEx(f) for f in form.fields]

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
