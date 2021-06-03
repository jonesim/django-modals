from django.forms import CheckboxInput, Textarea

class Toggle(CheckboxInput):
    template_name = 'widgets/toggle.html'

class TimyMCE(Textarea):
    template_name = 'widgets/tinymce.html'

