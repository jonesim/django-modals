from django.forms import CheckboxInput, Textarea


class Toggle(CheckboxInput):
    template_name = 'django_modals/widgets/toggle.html'
    crispy_kwargs = {'template': 'django_modals/fields/label_checkbox.html', 'field_class':'col-6 input-group-sm'}


class TinyMCE(Textarea):
    template_name = 'django_modals/widgets/tinymce.html'
    crispy_kwargs = {'label_class':'col-3 col-form-label-sm', 'field_class':'col-12 input-group-sm'}

