from crispy_forms.layout import Fieldset, HTML
from django.forms import all_valid
from django.forms.models import inlineformset_factory

from django_modals.form_helpers import RegularHelper
from django_modals.forms import BaseInlineCrispyFormSet, ProcessFormFields
from django_modals.modals import ModelFormModal


class ModelFormModalFormSet(ModelFormModal):

    template_name = 'django_modals/modal_formset_base.html'
    number_of_formsets = 1
    default_extra_rows = 1
    default_min_num = None
    default_absolute_max = None
    default_formset_can_delete = True
    default_formset_form = BaseInlineCrispyFormSet

    default_formset_title = ''
    default_formset_helper = RegularHelper

    def get_form_set_query(self):
        return None

    def form_setup(self, form, *_args, **_kwargs):
        formsets = []
        formset_layout = []
        for formset_number in range(1, self.number_of_formsets + 1):
            formset = self.setup_formset(formset_number=formset_number)
            formsets.append(formset)
            formset_layout += self.get_formset_layout(formset=formset, formset_number=formset_number)
        form.formsets = formsets
        return [f for f in form.fields.keys()] + formset_layout

    def get_variable_prefix(self, formset_number):
        if self.number_of_formsets == 1 and formset_number == 1:
            return ''
        return f'_{formset_number}'

    def get_formset_layout(self, formset, formset_number):
        html = formset.render()
        return [self.formset_label(formset_number=formset_number), HTML(html)]

    def formset_label(self, formset_number):
        variable_prefix = self.get_variable_prefix(formset_number=formset_number)
        return Fieldset(getattr(self, f'formset_title{variable_prefix}', self.default_formset_title))

    def formset_field_callback(self, f, **kwargs):
        return self.formfield_callback(f, **kwargs)

    def setup_formset(self, formset_number):
        variable_prefix = self.get_variable_prefix(formset_number=formset_number)

        processed_form_fields = ProcessFormFields(
            getattr(self, f'formset_fields{variable_prefix}'),
            widgets=getattr(self, f'formset_widgets{variable_prefix}', None),
            field_classes=getattr(self, f'formset_field_classes{variable_prefix}', None),
            labels=getattr(self, f'formset_labels{variable_prefix}', None),
            help_texts=getattr(self, f'formset_help_texts{variable_prefix}', None),
            error_messages=getattr(self, f'formset_error_messages{variable_prefix}', None))
        formset_factory = inlineformset_factory(
            parent_model=self.model,
            model=getattr(self, f'formset_model{variable_prefix}'),
            formset=getattr(self, f'formset_form{variable_prefix}', self.default_formset_form),
            extra=getattr(self, f'extra_rows{variable_prefix}', self.default_extra_rows),
            can_delete=getattr(self, f'formset_can_delete{variable_prefix}', self.default_formset_can_delete),
            min_num=getattr(self, f'min_num{variable_prefix}', self.default_min_num),
            absolute_max=getattr(self, f'absolute_max{variable_prefix}', self.default_absolute_max),
            fields=processed_form_fields.fields,
            **processed_form_fields.extra_kwargs(),
            formfield_callback=getattr(self, f'formset_field_callback{variable_prefix}', self.formset_field_callback))
        org_id = self.object.pk if hasattr(self, 'object') else None

        if self.request.method.lower() == 'post':
            data = self.request.POST
        else:
            data = None

        formset_helper = getattr(self, f'formset_helper{variable_prefix}', self.default_formset_helper)

        if org_id:
            query_set = getattr(self, f'get_form_set_query{variable_prefix}', self.get_form_set_query)()
            formset = formset_factory(data=data,
                                      queryset=query_set,
                                      instance=self.get_object(),
                                      helper_class=formset_helper,
                                      layout_field_params=processed_form_fields.layout_field_params)
        else:
            formset = formset_factory(data=data,
                                      helper_class=formset_helper,
                                      layout_field_params=processed_form_fields.layout_field_params)
        return formset

    def form_valid(self, form):
        formsets = form.formsets
        if all_valid(formsets):
            org_id = self.object.pk if hasattr(self, 'object') else None
            save_function = getattr(form, 'save', None)
            base_form_instance = None
            if save_function:
                base_form_instance = save_function()

            for formset in formsets:
                formset.instance = base_form_instance
                formset.save()
            self.post_save(created=org_id is None, form=form)
            if not self.response_commands:
                self.add_command('reload')
            return self.command_response()
        else:
            return self.form_invalid(form)
