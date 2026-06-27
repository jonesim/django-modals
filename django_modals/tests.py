"""Render tests guarding the native (crispy-free) Bootstrap 4 form rendering.

These assert that the structural Bootstrap classes the package produced under
crispy-forms are still emitted by the native renderer.
"""
from django import forms
from django.test import SimpleTestCase

from django_modals.fields import FieldEx
from django_modals.forms import CrispyForm
from django_modals.processes import PROCESS_VIEW


class RenderForm(CrispyForm):
    name = forms.CharField(required=True, help_text='Your name')
    active = forms.BooleanField(required=False)
    choice = forms.ChoiceField(choices=[(1, 'One'), (2, 'Two')])
    radio = forms.ChoiceField(choices=[(1, 'A'), (2, 'B')], widget=forms.RadioSelect, required=False)
    tags = forms.MultipleChoiceField(choices=[(1, 'A'), (2, 'B')], widget=forms.CheckboxSelectMultiple,
                                     required=False)
    doc = forms.FileField(required=False)


class FormRenderTests(SimpleTestCase):

    def test_text_field_markup(self):
        html = str(RenderForm())
        self.assertIn('form-group', html)
        self.assertIn('form-control', html)
        # crispy's widget class-name converter is preserved
        self.assertIn('textinput textInput', html)

    def test_required_marker_and_help_text(self):
        html = str(RenderForm())
        self.assertIn('asteriskField', html)
        self.assertIn('requiredField', html)
        self.assertIn('form-text', html)
        self.assertIn('Your name', html)

    def test_select_uses_custom_select(self):
        self.assertIn('custom-select', str(RenderForm()))

    def test_checkbox_uses_custom_control(self):
        html = str(RenderForm())
        self.assertIn('custom-control custom-checkbox', html)
        self.assertIn('custom-control-input', html)

    def test_radio_and_multiple_checkbox(self):
        html = str(RenderForm())
        self.assertIn('custom-radio', html)
        self.assertIn('custom-control-input', html)

    def test_errors_render_is_invalid(self):
        form = RenderForm(data={'choice': '1'})
        form.is_valid()
        html = str(form)
        self.assertIn('is-invalid', html)
        self.assertIn('invalid-feedback', html)

    def test_prepended_text_input_group(self):
        html = str(RenderForm(form_setup=lambda form, *a, **k: [FieldEx('name', prepended_text='£')]))
        self.assertIn('input-group', html)
        self.assertIn('input-group-prepend', html)
        self.assertIn('£', html)

    def test_buttons_render(self):
        html = str(RenderForm())
        self.assertIn('btn ', html)
        self.assertIn('django_modal.process_commands_lock', html)
        self.assertIn('Cancel', html)

    def test_view_mode_disables_fields(self):
        self.assertIn('disabled', str(RenderForm(process=PROCESS_VIEW)))

    def test_trigger_attribute(self):
        form = RenderForm()
        form.add_trigger('active', 'onchange', conditions=[])
        html = str(form)
        self.assertIn('django_modal.alter_form', html)
