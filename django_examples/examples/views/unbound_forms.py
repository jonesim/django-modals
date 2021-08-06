from django.forms import TextInput
from django.forms.fields import CharField, DateField
from django.forms.widgets import Textarea

from crispy_forms.layout import HTML
from show_src_code.modals import FormModal

from django_modals.forms import CrispyForm
from django_modals.widgets.jquery_datepicker import DatePicker
from django_modals.widgets.widgets import TinyMCE
from django_modals.fields import FieldEx

from .views import MainMenuTemplateView


class UnboundExamples(MainMenuTemplateView):

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'button_menu.html', ).add_items(
            ('unbound_modal', 'Simple'),
            ('unbound_payment', 'Field Configuration'),
            ('unbound_layout', 'Field Layout'),
        )


class EnquiryForm(CrispyForm):

    Name = CharField()
    Address = CharField(widget=Textarea)
    Enquiry = CharField(widget=TinyMCE)


class UnboundModal(FormModal):
    form_class = EnquiryForm
    modal_title = 'Enquiry Form'

    def form_valid(self, form):
        return self.message(f'Cleaned data - {form.cleaned_data}', 'Form Valid')


class PaymentForm(CrispyForm):

    # Can be used as a global widget - not normally defined in form
    class CurrencyWidget(TextInput):
        crispy_kwargs = {'prepended_text': '£'}

    # Can be used as a global DateField - not normally defined in form
    class DateFieldEx(DateField):
        def __init__(self, *args, **kwargs):
            self.widget = DatePicker
            super().__init__(*args, **kwargs)

    # Normal form definition

    class Meta:
        layout_field_params = {'Amount_form_config': {'prepended_text': 'Form £'}}

    Date = DateField(widget=DatePicker)
    Date_field = DateFieldEx()
    Amount_form_config = CharField()
    Amount_view_config = CharField()
    Amount_widget = CharField(widget=CurrencyWidget)


class UnboundPaymentModal(FormModal):
    form_class = PaymentForm
    modal_title = 'Payment Form'

    @staticmethod
    def form_setup(form, *_args, **_kwargs):
        pass
        # form.layout_field_params = {'Amount_view_config': {'prepended_text': 'View £'}}

    def form_valid(self, form):
        return self.message(f'Cleaned data - {form.cleaned_data}', 'Form Valid')


class EnquiryDetailForm(CrispyForm):

    class Meta:
        layout_field_params = {
            'Name': {'prepended_text': 'Name'}
        }

    Name = CharField()
    Address = CharField(widget=Textarea)
    Enquiry = CharField(widget=TinyMCE)


class UnboundLayoutModal(FormModal):
    form_class = EnquiryForm
    modal_title = 'Enquiry Form'

    def form_valid(self, form):
        return self.message(f'Cleaned data - {form.cleaned_data}', 'Form Valid')

    @staticmethod
    def form_setup(_form, *_args, **_kwargs):
        return [HTML('Explicit placement of fields'),
                FieldEx('Name', prepended_text='Name'),
                FieldEx('Address', label_class='col-3 col-form-label-sm', field_class='col-12 input-group-sm'),
                HTML('Enter notes here'),
                FieldEx('Enquiry', label_class='col-3 col-form-label-sm', field_class='col-12 input-group-sm')]
