"""Render tests guarding the native (crispy-free) Bootstrap 4 form rendering.

These assert that the structural Bootstrap classes the package produced under
crispy-forms are still emitted by the native renderer.
"""
from django import forms
from django.test import SimpleTestCase, override_settings

from django_modals.fields import FieldEx
from django_modals.forms import CrispyForm, widget_field_class, widget_field_kwargs
from django_modals.processes import PROCESS_VIEW
from django_modals.widgets.colour_picker import ColourPickerFieldEx, ColourPickerWidget
from django_modals.widgets.jquery_datepicker import DatePicker
from django_modals.widgets.tom_select import TomSelect, TomSelectMultiple


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
        # the onclick payload is single-quoted so its JSON double-quotes survive,
        # and the single_quote flag must not leak out as an HTML attribute
        self.assertIn("onclick='", html)
        self.assertNotIn('single-quote=', html)

    def test_view_mode_disables_fields(self):
        self.assertIn('disabled', str(RenderForm(process=PROCESS_VIEW)))

    def test_trigger_attribute(self):
        form = RenderForm()
        form.add_trigger('active', 'onchange', conditions=[])
        html = str(form)
        self.assertIn('django_modal.alter_form', html)

    def test_non_field_errors_render(self):
        class CleanForm(RenderForm):
            def clean(self):
                raise forms.ValidationError('Dates overlap')

        form = CleanForm(data={'name': 'x', 'choice': '1'})
        form.is_valid()
        html = str(form)
        self.assertIn('alert-danger', html)
        self.assertIn('Dates overlap', html)
        # the alert is the form's first child, as crispy rendered it
        self.assertLess(html.index('<form'), html.index('alert-danger'))
        self.assertLess(html.index('Dates overlap'), html.index('div_id_name'))

    def test_no_error_alert_without_errors(self):
        self.assertNotIn('alert-danger', str(RenderForm()))


class LegacyCrispyDate(DatePicker):
    crispy_kwargs = {'prepended_text': 'LEGACY'}


class LegacyCrispyWidget(forms.TextInput):
    crispy_kwargs = {'prepended_text': 'PLAIN_LEGACY'}


class WidgetAttributeTests(SimpleTestCase):
    """modal_kwargs / modal_field_class replace crispy_kwargs / crispy_field_class; the old
    names must keep working in both directions during the deprecation period."""

    def test_legacy_name_on_subclass_overrides_package_widget(self):
        self.assertEqual(widget_field_kwargs(LegacyCrispyDate()), {'prepended_text': 'LEGACY'})

        class Form(CrispyForm):
            d = forms.DateField(widget=LegacyCrispyDate)
        self.assertIn('LEGACY', str(Form()))

    def test_legacy_name_on_plain_widget(self):
        self.assertEqual(widget_field_kwargs(LegacyCrispyWidget()), {'prepended_text': 'PLAIN_LEGACY'})

    def test_new_name_on_subclass_overrides_package_widget(self):
        class NewDate(DatePicker):
            modal_kwargs = {'prepended_text': 'NEW'}
        self.assertEqual(widget_field_kwargs(NewDate()), {'prepended_text': 'NEW'})

    def test_package_widgets_expose_legacy_aliases(self):
        widget = ColourPickerWidget()
        self.assertEqual(widget.crispy_kwargs, ColourPickerWidget.modal_kwargs)
        self.assertIs(widget.crispy_field_class, ColourPickerFieldEx)
        self.assertIs(widget_field_class(widget), ColourPickerFieldEx)

    def test_instance_assignment_of_legacy_name(self):
        widget = DatePicker()
        widget.crispy_kwargs = {'prepended_text': 'INSTANCE'}
        self.assertEqual(widget_field_kwargs(widget), {'prepended_text': 'INSTANCE'})

    def test_default_field_class(self):
        self.assertIs(widget_field_class(forms.TextInput()), FieldEx)
        self.assertEqual(widget_field_kwargs(forms.TextInput()), {})


class TomSelectRenderTests(SimpleTestCase):
    """The Tom Select widget renders a plain <select> plus an inittomselect() bootstrap call,
    reusing the same select2 server contract (no Python dispatch changes)."""

    def test_widget_renders_select_and_init(self):
        html = TomSelect(choices=[(1, 'One'), (2, 'Two')]).render('company', None, attrs={'id': 'id_company'})
        self.assertIn('<select name="company"', html)
        self.assertIn('tom_select_widget.inittomselect(', html)
        self.assertIn('"id_company"', html)

    def test_ajax_flag_flows_to_init(self):
        html = TomSelect(attrs={'ajax': True}).render('company', None, attrs={'id': 'id_company'})
        # the init call's second positional arg (ajax) is rendered truthy
        self.assertIn('inittomselect(\n', html)
        self.assertIn('true', html)

    def test_multiple_widget_renders(self):
        html = TomSelectMultiple(attrs={'ajax': True}, choices=[(1, 'One')]).render(
            'company', None, attrs={'id': 'id_company'})
        self.assertIn('<select name="company"', html)
        self.assertIn('multiple', html)
        self.assertIn('inittomselect(', html)


@override_settings(CSS_FRAMEWORK='bootstrap5')
class Bootstrap5RenderTests(SimpleTestCase):
    """Selecting bootstrap5 swaps the html_classes renderer to the BS5 profile —
    form-select / form-check / mb-3 / native file input, and none of the BS4
    custom-* / form-group markup."""

    def test_bootstrap5_tokens_present(self):
        html = str(RenderForm())
        self.assertIn('form-select', html)       # <select> (was custom-select)
        self.assertIn('form-check', html)         # checkbox/radio wrapper
        self.assertIn('form-check-input', html)
        self.assertIn('mb-3', html)               # field wrapper (was form-group)
        self.assertIn('form-control', html)       # text + file inputs

    def test_bootstrap5_drops_bootstrap4_markup(self):
        html = str(RenderForm())
        self.assertNotIn('custom-control', html)
        self.assertNotIn('custom-select', html)
        self.assertNotIn('custom-file', html)
        self.assertNotIn('form-group', html)

    def test_bootstrap5_errors_still_invalid(self):
        form = RenderForm(data={'choice': '1'})
        form.is_valid()
        html = str(form)
        self.assertIn('is-invalid', html)
        self.assertIn('invalid-feedback', html)

    def test_bootstrap5_required_markers_kept(self):
        html = str(RenderForm())
        self.assertIn('requiredField', html)
        self.assertIn('asteriskField', html)
