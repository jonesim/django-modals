[![PyPI version](https://badge.fury.io/py/django-nested-modals.svg)](https://badge.fury.io/py/django-nested-modals)

# django-nested-modals

Bootstrap nested modals with AJAX form handling for Django. Modals are class-based views — they handle GET (render the modal) and POST (process buttons/forms) via AJAX, with responses returned as JSON command arrays.

## Installation

```bash
pip install django-nested-modals
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'bootstrap_modals',
]
```

Add to your base template:

```html
<script src="{% static 'django_modals/js/modals.js' %}"></script>
<link rel="stylesheet" type="text/css" href="{% static 'django_modals/css/modals.css' %}"/>
```

---

## Quick Start

### 1. Define a modal view

```python
# views.py
from django_modals.modals import ModelFormModal

class CompanyModal(ModelFormModal):
    model = Company
    form_fields = ['name', 'active']
    modal_title = ['New Company', 'Edit Company']
```

### 2. Wire up a URL

```python
# urls.py
path('modal/company/<slug:slug>/', CompanyModal.as_view(), name='company_modal'),
```

### 3. Trigger it from a template

```django
{% load modal_tags %}
{% show_modal 'company_modal' 'pk-1' %}          {# edit pk=1 #}
{% show_modal 'company_modal' 'pk-0' %}          {# create new #}
```

---

## Modal Types

### `Modal` — simple content modal

Use for messages, confirmations, or any custom HTML content.

```python
from django_modals.modals import Modal
from django_modals.helper import modal_button

class InfoModal(Modal):
    modal_title = 'Information'

    def modal_content(self):
        return '<p>This action cannot be undone.</p>'

    def get_modal_buttons(self):
        return [modal_button('OK', 'close', 'btn-success')]
```

### `TemplateModal` — modal from a template file

```python
from django_modals.modals import TemplateModal

class HelpModal(TemplateModal):
    modal_title = 'Help'
    modal_template = 'myapp/help_modal.html'

    def modal_context(self):
        return {'section': self.slug.get('section', 'general')}
```

### `FormModal` — non-model form

```python
from django_modals.modals import FormModal

class ContactModal(FormModal):
    form_class = ContactForm
    modal_title = 'Contact Us'

    def form_valid(self, form):
        send_email(form.cleaned_data)
        return self.command_response('reload')
```

### `ModelFormModal` — CRUD modal for a model

The most common modal type. Automatically handles create, edit, view, and delete.

```python
from django_modals.modals import ModelFormModal
from django_modals.processes import PERMISSION_AUTHENTICATED, PERMISSION_STAFF

class PersonModal(ModelFormModal):
    model = Person
    form_fields = ['first_name', 'surname', 'email', 'company']
    modal_title = ['New Person', 'Edit Person', 'View Person']
    permission_create = PERMISSION_AUTHENTICATED
    permission_edit = PERMISSION_AUTHENTICATED
    permission_delete = PERMISSION_STAFF
```

### `MultiFormModal` — multiple independent forms in one modal

```python
from django_modals.modals import MultiFormModal, MultiForm

class NewAccountModal(MultiFormModal):
    modal_title = 'Create Account'
    forms = [
        MultiForm(Company, ['name', 'active']),
        MultiForm(Person, ['first_name', 'surname', 'email']),
    ]

    def forms_valid(self, valid_forms):
        company = valid_forms['CompanyForm'].save()
        person = valid_forms['PersonForm']
        person.instance.company = company
        person.save()
        return self.command_response('reload')
```

---

## URL Slug System

State is passed via a single URL slug encoded as alternating key-value pairs. The slug is parsed into `self.slug` dict inside the modal.

```
pk-1                 →  {'pk': '1'}              edit pk=1
pk-0                 →  {}                       create new
pk-1-modal-view      →  {'pk': '1', ...}         view (read-only)
pk-1-modal-viewedit  →  {'pk': '1', ...}         view with edit button
pk-1-modal-delete    →  {'pk': '1', ...}         delete confirmation
section-help         →  {'section': 'help'}      arbitrary key-value
```

In the URL conf, use `<slug:slug>` for standard slugs or `<str:slug>` when values contain uppercase or special characters.

```python
urlpatterns = [
    path('modal/person/<slug:slug>/', PersonModal.as_view(), name='person_modal'),
]
```

---

## Processes and Permissions

Each modal operation is a *process*. Permissions control who can invoke each process.

### Process constants (`django_modals.processes`)

| Constant | Value | Description |
|---|---|---|
| `PROCESS_CREATE` | 0 | Create new object |
| `PROCESS_EDIT` | 1 | Edit existing object |
| `PROCESS_VIEW` | 2 | Read-only view |
| `PROCESS_DELETE` | 3 | Delete object |
| `PROCESS_EDIT_DELETE` | 4 | Edit with delete button |
| `PROCESS_VIEW_EDIT` | 5 | Read-only with edit button |

### Permission constants

| Constant | Description |
|---|---|
| `PERMISSION_OFF` | No restriction |
| `PERMISSION_DISABLE` | Always disabled |
| `PERMISSION_AUTHENTICATED` | Logged-in users only |
| `PERMISSION_STAFF` | Staff/superusers only |
| `PERMISSION_METHOD` | Delegate to `permission(user, process)` method |

```python
from django_modals.processes import (
    PERMISSION_OFF, PERMISSION_AUTHENTICATED,
    PERMISSION_STAFF, PERMISSION_METHOD
)

class CompanyModal(ModelFormModal):
    model = Company
    form_fields = ['name', 'active']
    permission_create = PERMISSION_AUTHENTICATED
    permission_edit = PERMISSION_AUTHENTICATED
    permission_delete = PERMISSION_STAFF
    permission_view = PERMISSION_OFF

    # Used when permission_X = PERMISSION_METHOD
    @staticmethod
    def permission(user, process):
        return user.groups.filter(name='editors').exists()
```

---

## ModelFormModal Reference

### Class attributes

| Attribute | Type | Description |
|---|---|---|
| `model` | Model class | Required |
| `form_fields` | list | Field names to include |
| `form_class` | Form class | Override auto-generated form |
| `modal_title` | str or list | Single title, or `[create, edit, view]` |
| `size` | `'sm'` / `'md'` / `'lg'` | Modal dialog size (default `'lg'`) |
| `labels` | dict | Field label overrides |
| `help_texts` | dict | Field help text overrides |
| `widgets` | dict | Widget overrides |
| `field_classes` | dict | Form field class overrides |
| `error_messages` | dict | Error message overrides |
| `permission_create` | constant | Create permission |
| `permission_edit` | constant | Edit permission |
| `permission_view` | constant | View permission |
| `permission_delete` | constant | Delete permission |
| `delete_message` | str | Confirmation message for delete |
| `delete_title` | str | Title for delete confirmation |
| `focus` | bool | Auto-focus first field (default `True`) |
| `lazy` | bool | Load modal content via AJAX (default `False`) |

### Hook methods

```python
class PersonModal(ModelFormModal):
    model = Person
    form_fields = ['first_name', 'surname', 'company']

    @staticmethod
    def form_setup(form, **kwargs):
        """Customise form fields before rendering — runs on GET and invalid POST."""
        form.fields['company'].queryset = Company.objects.filter(active=True)

    def form_valid(self, form):
        """Override save logic. Must return a command response."""
        instance = form.save()
        return self.command_response('reload')

    def post_save(self, created, form):
        """Runs after save, before the response is built."""
        if created:
            notify_team(form.instance)

    def object_delete(self):
        """Runs after the object is deleted."""
        audit_log(self.object)
```

---

## MultiFormModal Reference

Forms are defined with `MultiForm` instances. Each `MultiForm` accepts the same field-configuration arguments as `ModelFormModal`.

```python
MultiForm(
    model,
    fields,
    form_id=None,        # Defaults to '<ModelName>Form'
    labels={},
    help_texts={},
    widgets={},
    field_classes={},
    error_messages={},
)
```

Override methods on the modal:

```python
class AccountModal(MultiFormModal):
    forms = [
        MultiForm(Company, ['name']),
        MultiForm(Person, ['first_name', 'surname']),
    ]

    def form_setup(self, form, **kwargs):
        """Called for each form individually. Return a layout or None."""
        if form.form_id == 'PersonForm':
            form.fields['surname'].required = True
        return None

    def get_instances(self, form_id):
        """Return a model instance for edit mode."""
        if form_id == 'CompanyForm':
            return Company.objects.get(pk=self.slug.get('pk'))

    def forms_valid(self, valid_forms):
        company = valid_forms['CompanyForm'].save()
        person = valid_forms['PersonForm']
        person.instance.company = company
        person.save()
        return self.command_response('reload')
```

---

## Forms

### `ModelCrispyForm`

The default base form used by `ModelFormModal`. Inherits from `ModelForm` and applies crispy-forms layout automatically. Use it directly when you need a custom `form_class`:

```python
from django_modals.forms import ModelCrispyForm

class PersonForm(ModelCrispyForm):
    class Meta:
        model = Person
        fields = ['first_name', 'surname', 'email']

class PersonModal(ModelFormModal):
    form_class = PersonForm
```

### `CrispyForm`

For non-model forms with crispy rendering:

```python
from django_modals.forms import CrispyForm
from django import forms

class SearchForm(CrispyForm):
    query = forms.CharField()
    active_only = forms.BooleanField(required=False)
```

### Advanced field configuration with `FieldEx`

Pass a tuple `(field_name, options_dict)` in `form_fields` for per-field configuration:

```python
from django_modals.helper import FieldEx

class CompanyModal(ModelFormModal):
    model = Company
    form_fields = [
        'name',
        ('status', {'label': 'Current Status', 'help_text': 'Active or inactive'}),
        FieldEx('notes', template='custom_field.html'),
    ]
```

---

## Widgets

```python
from django_modals.widgets.select2 import Select2, Select2Multiple
from django_modals.widgets.colour_picker import ColourPickerWidget
from django_modals.widgets.datepicker import JQueryDatepickerWidget
from django_modals.widgets.month_picker import MonthPickerWidget
```

### Select2

```python
class CompanyModal(ModelFormModal):
    model = Company
    form_fields = ['name', 'tags', 'owner']
    widgets = {
        'tags': Select2Multiple,
        'owner': Select2,
    }
```

**AJAX-powered Select2** — define a `select2_<fieldname>` method on the modal to filter results dynamically:

```python
def select2_owner(self, search, **kwargs):
    qs = Person.objects.filter(name__icontains=search)
    return [(p.pk, str(p)) for p in qs]
```

---

## Template Tags

```django
{% load modal_tags %}

{# Link that opens a modal #}
{% show_modal 'url_name' 'pk-1' %}
{% show_modal 'url_name' 'pk-1' css_class='btn btn-primary' label='Edit' %}

{# AJAX button that calls a method on the current modal #}
{% modal_button_method 'Save Draft' 'save_draft' %}

{# Delete button #}
{% modal_delete 'url_name' slug='pk-1' text='Delete' %}
```

---

## AJAX Commands

Modal button handlers and `form_valid` must return a command response. Commands are processed client-side by `ajax_helpers.process_commands`.

```python
# Close the modal and reload the page
return self.command_response('reload')

# Close the modal only
return self.command_response('close')

# Redirect
return self.command_response('redirect', url='/dashboard/')

# Update a DOM element without closing the modal
self.add_command('html', selector='#status', html='<span>Saved</span>')
return self.command_response()

# Replace the modal content
return self.command_response('overwrite_modal', html=rendered_html)
```

Custom button handlers are methods named `button_<name>`:

```python
class ReportModal(TemplateModal):
    modal_title = 'Report'
    modal_template = 'report.html'

    def button_export(self, **kwargs):
        data = generate_csv(self.slug.get('pk'))
        return self.command_response('save_file', filename='report.csv', data=data)
```

---

## Lazy Loading

Set `lazy = True` on a modal to defer content loading until the modal is opened. Useful for slow queries:

```python
class HeavyReportModal(TemplateModal):
    lazy = True
    modal_title = 'Report'
    modal_template = 'report.html'
```

---

## JSON Field Mixin

`JsonFieldMixin` expands a `JSONField` into individually editable typed form fields:

```python
from django_modals.modals import ModelFormModal, JsonFieldMixin
from django import forms

class CompanyModal(JsonFieldMixin, ModelFormModal):
    model = Company
    form_fields = ['name']
    json_field = 'extra'
    json_field_config = {
        'notes': (forms.CharField, {'required': False, 'label': 'Notes'}),
        'priority': (forms.ChoiceField, {
            'choices': [('low', 'Low'), ('high', 'High')],
            'required': False,
        }),
    }
```

The modal renders an "Add field" dropdown; selecting a key adds that field to the form. On save, all values are packed back into the JSON column.

---

## Development / Example Project

```bash
docker-compose up
```

Django app runs at `http://localhost:8007`. See `django_examples/modal_examples/views/` for working examples of every modal type.

```bash
# Run tests
cd django_examples
python manage.py test django_modals
```
