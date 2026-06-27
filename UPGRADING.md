# Upgrading django-nested-modals — the crispy-forms removal release

This release removes the hard dependency on **django-crispy-forms**. `django-modals` now
renders its own form/field HTML natively. Output is **Bootstrap 4** and is visually equivalent
to the previous crispy-rendered output, so most projects upgrade with only a few mechanical
import changes.

> **Bootstrap 5 is not yet supported.** This release delivers BS4 parity without crispy. A
> `MODAL_BOOTSTRAP_VERSION` setting and a BS5 template pack are planned for a later release.

---

## TL;DR checklist

- [ ] Remove `django-crispy-forms` (and `crispy-bootstrap4`, if present) from your requirements.
- [ ] Remove `'crispy_forms'` from `INSTALLED_APPS` and delete any `CRISPY_TEMPLATE_PACK` /
      `CRISPY_*` settings.
- [ ] Replace `from crispy_forms.layout import HTML, Div, Layout, Fieldset` with
      `from django_modals.layout import HTML, Div, Layout, Fieldset`.
- [ ] Replace `from crispy_forms.layout import Field` with
      `from django_modals.fields import FieldEx` (and use `FieldEx` in place of `Field`).
- [ ] Rename widget attributes `crispy_kwargs` → `modal_kwargs` and
      `crispy_field_class` → `modal_field_class` (old names still work but are deprecated).
- [ ] Update any custom field templates that used `{% load crispy_forms_field %}` /
      `{% crispy_field %}` (see below).
- [ ] Update custom `FieldEx` / `Div` subclasses that overrode crispy render methods (see below).
- [ ] Run your modals and check forms render correctly.

Nothing in the **modal class API** changed: `ModelFormModal`, `form_fields`, `helper_class`,
`form_setup`, `modal_title`, `prepended_text`, `no_buttons`, permissions, buttons, Select2,
triggers, formsets, etc. all behave exactly as before.

---

## 1. Requirements & settings

**requirements / pyproject** — drop crispy:

```diff
- django-crispy-forms
- crispy-bootstrap4        # if you had it
```

**settings.py**:

```diff
 INSTALLED_APPS = [
     ...
     'django_modals',
-    'crispy_forms',
     ...
 ]

-CRISPY_TEMPLATE_PACK = 'bootstrap4'
```

(If you set `CRISPY_CLASS_CONVERTERS`, it is still honoured by the renderer but no longer
required.)

---

## 2. Layout object imports

The layout helpers used to come from crispy. They are now provided by `django_modals` and have
the **same names and constructor signatures**, so usually it's just the import line that changes.

```diff
- from crispy_forms.layout import HTML, Div, Layout
+ from django_modals.layout import HTML, Div, Layout

- from crispy_forms.layout import Field
+ from django_modals.fields import FieldEx
```

| Was (crispy) | Now |
|---|---|
| `crispy_forms.layout.HTML` | `django_modals.layout.HTML` |
| `crispy_forms.layout.Div` | `django_modals.layout.Div` |
| `crispy_forms.layout.Layout` | `django_modals.layout.Layout` |
| `crispy_forms.layout.Fieldset` | `django_modals.layout.Fieldset` |
| `crispy_forms.layout.Field` | `django_modals.fields.FieldEx` |

Example:

```diff
  def form_setup(self, form, *args, **kwargs):
-     return Field(*form.Meta.fields), HTML(render_to_string('people.html', {...}))
+     return FieldEx(*form.Meta.fields), HTML(render_to_string('people.html', {...}))
```

**Removed layout helpers:** `Flex` and `FieldNoLabel` were unused and have been deleted.
`MultiFieldRow`, `MultiField`, and `Label` remain (import from `django_modals.fields`).

---

## 3. Widget attributes: `crispy_kwargs` → `modal_kwargs`

Custom widgets that fed field-layout options to the renderer used `crispy_kwargs` /
`crispy_field_class`. Rename them:

```diff
  class CurrencyWidget(TextInput):
-     crispy_kwargs = {'prepended_text': '£', 'field_class': 'col-md-3 input-group-sm'}
+     modal_kwargs = {'prepended_text': '£', 'field_class': 'col-md-3 input-group-sm'}

  class ColourPickerWidget(TextInput):
-     crispy_field_class = ColourPickerFieldEx
+     modal_field_class = ColourPickerFieldEx
```

> **Backward compatible:** the old `crispy_kwargs` / `crispy_field_class` names are still read as a
> fallback, so widgets keep working unchanged — but rename them when convenient.

---

## 4. Custom field templates

If you wrote your own field template (e.g. referenced via a widget's
`modal_kwargs = {'template': '...'}`), update the crispy tags to the new `modal_forms` library:

```diff
- {% load crispy_forms_field %}
+ {% load modal_forms %}

-     {% crispy_field field 'class' 'custom-select' %}
+     {% modal_field field 'class' 'custom-select' %}

-     {% include 'bootstrap4/layout/help_text_and_errors.html' %}
+     {% include 'django_modals/forms/bootstrap4/help_text_and_errors.html' %}
```

`modal_forms` provides the field-branching filters you may use:
`is_checkbox`, `is_select`, `is_radioselect`, `is_checkboxselectmultiple`, `is_file`, `optgroups`.

The package's own field templates now live under
`django_modals/templates/django_modals/forms/bootstrap4/` (`field.html`, `checkbox.html`,
`prepended_appended_text.html`, plus the help/error/radio partials).

**Renamed/removed package templates** — update references if you pointed at them directly:

| Old path | New path |
|---|---|
| `django_modals/fields/label_checkbox.html` | `django_modals/forms/bootstrap4/checkbox.html` |
| `django_modals/formset/prepended_appended_text.html` | `django_modals/forms/bootstrap4/prepended_appended_text.html` |

Also note the context variables for input-group text were renamed inside templates:
`crispy_prepended_text` → `prepended_text`, `crispy_appended_text` → `appended_text`.

---

## 5. Custom subclasses that overrode crispy render methods

If you subclassed `FieldEx` or `Div` and overrode `render(...)`, the signature changed from the
crispy form (`render(self, form, form_style, context, template_pack=...)`) to the native form
**`render(self, form, context)`**:

```diff
  class DivEx(Div):
-     def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
-         ...
-         fields = self.get_rendered_fields(form, form_style, context, template_pack, **kwargs)
-         return render_to_string(self.get_template_name(template_pack), {'div': self, 'fields': fields})
+     def render(self, form, context):
+         ...
+         return super().render(form, context)
```

If you overrode `FieldEx.get_prepended_appended_template_name`, it **no longer takes a
`template_pack` argument** and should return a full template path:

```diff
  class ColourPickerFieldEx(FieldEx):
-     @staticmethod
-     def get_prepended_appended_template_name(template_pack):
-         return "django_modals/widgets/colour_picker_append.html"
+     def get_prepended_appended_template_name(self):
+         return "django_modals/widgets/colour_picker_append.html"
```

`FieldEx` is now a lightweight layout spec (not a crispy `Field` subclass). It still supports the
same constructor — `FieldEx(name, prepended_text=..., field_class=..., wrapper_class=...,
css_class=..., style=...)` — and adds `update_attributes(**attrs)`.

---

## 6. Things that did NOT change

- All modal classes and their attributes/hooks (`form_fields`, `widgets`, `labels`,
  `form_setup`, `post_save`, `modal_title` as `[create, edit, view]`, permissions, lazy loading,
  JSON-field mixin, Select2 + `select2_<field>` search, `add_trigger`, formsets).
- The helper classes (`HorizontalHelper`, `SmallHelper`, `RegularHelper`, `TwoColumnHelper`, …) —
  same names, same grid classes; import from `django_modals.form_helpers` as before.
- Public class/function names retain "Crispy" for compatibility: `CrispyForm`,
  `ModelCrispyForm`, `BaseInlineCrispyFormSet`, `CrispyFormMixin`, `helper.crispy_modal_link`.
- Rendered Bootstrap 4 markup (same `form-group` / `form-control` / `custom-select` /
  `custom-control` / `input-group` / `btn` classes).

---

## 7. Verifying your project after upgrade

1. `pip uninstall django-crispy-forms` — your app should still import and run.
2. Open each modal type you use and confirm fields, labels, required markers, help text, input
   groups, checkboxes/radios, file inputs, custom widgets, and view/disabled mode all render.
3. Submit a form with validation errors and confirm `is-invalid` / `invalid-feedback` still show.
4. If you have a test suite, render your forms and assert on the Bootstrap classes you depend on.
