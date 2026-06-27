"""Form layout helpers.

Plain config objects (formerly crispy ``FormHelper`` subclasses) carrying the
grid/spacing class strings the renderer and field templates read.  Attribute
names are unchanged so existing ``helper_class = SmallHelper`` style usage keeps
working.
"""


class WrapperHelper:
    use_custom_control = True
    form_show_errors = True
    form_show_labels = True
    error_text_inline = True
    help_text_inline = False
    disable_csrf = False
    form_tag = True
    form_method = 'post'
    form_class = ''
    label_class = ''
    field_class = ''
    template = None
    form_id = None

    def __init__(self, form=None):
        self.form = form
        if hasattr(self, 'form_attrs'):
            self.attrs = self.form_attrs
        else:
            self.attrs = {}


class InlineFormset(WrapperHelper):
    template = 'django_modals/multi_form/table_formset.html'
    disable_csrf = True


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


class HorizontalNoEnterHelper(HorizontalHelper):
    form_attrs = {'no_enter': True}
