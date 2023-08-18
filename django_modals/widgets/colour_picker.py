from django.forms.widgets import TextInput

from django_modals.fields import FieldEx


class ColourPickerFieldEx(FieldEx):
    @staticmethod
    def get_prepended_appended_template_name(template_pack):
        return "django_modals/widgets/colour_picker_append.html"


class ColourPickerWidget(TextInput):
    template_name = 'django_modals/widgets/colour_picker.html'
    formset_field_template = "django_modals/widgets/colour_picker_append.html"

    crispy_kwargs = {'field_class': 'col-sm-12 col-md-4 col-lg-3',
                     'appended_text': ' ',
                     'input_size': 'input-group-sm'}
    crispy_field_class = ColourPickerFieldEx

    def __init__(self, opacity=False, swatches=None, *args, **kwargs):
        self.opacity = opacity
        self.swatches = swatches
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['opacity'] = self.opacity
        context['swatches'] = self.swatches
        return context
