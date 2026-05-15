from django.forms import ChoiceField

from django_modals.widgets.select2 import Select2


class JsonFieldMixin:
    """
    Mixin for ModelFormModal that turns a JSONField into a dynamic set of typed form fields.

    Class attributes on the modal view:
        json_field       -- name of the JSONField on the model (default: 'extra')
        json_field_config -- dict of {key: (FieldClass, field_kwargs)} defining the allowed keys

    The mixin injects an "Add Option" Select2 dropdown (named after json_field) that lists
    keys not yet present in the JSON.  Selecting one triggers an AJAX form refresh that adds
    the corresponding field.  On save, all dynamic field values are packed back into the JSON.

    The AJAX handler is resolved dynamically via __getattr__ so that any json_field name
    routes correctly without needing a concrete method per field name.

    Cooperative form_setup: subclasses may define their own form_setup and call
    super().form_setup(form, **kwargs) to preserve the JSON field injection.
    """

    json_field = 'extra'
    json_field_config = {}

    # ------------------------------------------------------------------
    # AJAX routing
    # ------------------------------------------------------------------

    def __getattr__(self, name):
        if name == f'select2_{self.json_field}_selected':
            return self._json_field_add_handler
        raise AttributeError(name)

    def _json_field_add_handler(self, **_kwargs):
        form = self.get_form()
        form.clear_errors()
        return self.refresh_form(form)

    # ------------------------------------------------------------------
    # Field helpers
    # ------------------------------------------------------------------

    def json_get_field(self, key, **overrides):
        field_class, field_kwargs = self.json_field_config[key]
        kwargs = dict(field_kwargs)
        kwargs.update(overrides)
        return field_class(**kwargs)

    def _json_build_add_choices(self, form):
        current_keys = set(getattr(form.instance, self.json_field, {}).keys())
        post_keys = set(self.request.POST.keys()) if self.request.method.lower() == 'post' else set()
        choices = [(None, '-')]
        for key in self.json_field_config:
            if key not in current_keys and key not in post_keys:
                label = self.json_field_config[key][1].get('label', key)
                choices.append((key, label))
        return choices

    def _json_inject_add_field(self, form):
        form.fields[self.json_field] = ChoiceField(
            choices=self._json_build_add_choices(form),
            label='Add Option',
            widget=Select2(attrs={'tags': True, 'selected_ajax': 'form'}),
            required=False,
        )

    def _json_process_fields(self, form):
        self._json_inject_add_field(form)
        json_data = getattr(form.instance, self.json_field, {})

        if self.request.method.lower() == 'post':
            for key in self.json_field_config:
                if key in self.request.POST:
                    form.fields[key] = self.json_get_field(key)
            new_key = self.request.POST.get(self.json_field)
            if new_key and new_key in self.json_field_config:
                form.data = self.request.POST.dict()
                form.fields[new_key] = self.json_get_field(new_key)
                initial = self.json_field_config[new_key][1].get('initial')
                if initial is not None:
                    form.data[new_key] = initial
                form.data.pop(self.json_field, None)
        else:
            for key, value in json_data.items():
                if key in self.json_field_config:
                    form.fields[key] = self.json_get_field(key, initial=value)

    # ------------------------------------------------------------------
    # Form hooks
    # ------------------------------------------------------------------

    def form_setup(self, form, **kwargs):
        parent = getattr(super(), 'form_setup', None)
        result = parent(form, **kwargs) if parent else None
        self._json_process_fields(form)
        return result

    def form_valid(self, form):
        json_data = {
            key: form.cleaned_data[key]
            for key in self.json_field_config
            if key in form.cleaned_data and form.cleaned_data[key] not in ('', None)
        }
        setattr(form.instance, self.json_field, json_data)
        return super().form_valid(form)
