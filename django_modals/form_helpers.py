from crispy_forms.helper import FormHelper
from crispy_forms.utils import TEMPLATE_PACK


class WrapperHelper(FormHelper):
    def get_attributes(self, template_pack=TEMPLATE_PACK):
        items = super().get_attributes(template_pack)
        if hasattr(self, 'wrapper_class'):
            items['wrapper_class'] = self.wrapper_class
        return items


class TwoColumnHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-4 col-form-label-sm'
    field_class = 'col-md-8 input-group-sm'
    form_class = 'form-horizontal'
    wrapper_class = 'col-lg-6'
    fields_wrap_class = 'row'
    disable_csrf = True


class HorizontalHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 col-lg-6 input-group-sm'
    form_class = 'form-horizontal'
    disable_csrf = True


class SmallHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 input-group-sm'
    form_class = 'form-horizontal'
    disable_csrf = True


class RegularHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = ''
    field_class = 'input-group-sm'
    form_class = ''
    disable_csrf = True
    auto_placeholder = True


class TwoColumnRegularHelper(RegularHelper):
    wrapper_class = 'col-lg-6'
    fields_wrap_class = 'form-row'


class NoLabelsRegularHelper(RegularHelper):
    form_show_labels = False
