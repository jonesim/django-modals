[![PyPI version](https://badge.fury.io/py/django-nested-modals.svg)](https://badge.fury.io/py/django-nested-modals)

## Help / Quick Start

### 1) Install

```bash
pip install django-nested-modals
```

### 2) Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    "bootstrap_modals",
]
```

### 3) Include modal assets in your base template

```django
{% load static %}
<script src="{% static 'django_modals/js/modals.js' %}"></script>
<link rel="stylesheet" type="text/css" href="{% static 'django_modals/css/modals.css' %}"/>
```

### 4) Minimal modal example

```python
from show_src_code.modals import Modal
from django_modals.url_helper import get_urls


class HelloModal(Modal):
    def modal_content(self):
        return "Hello from django-nested-modals"


urlpatterns = get_urls(__name__)
```

```django
{% load modal_tags %}
{% show_modal 'hello_modal' button='Open modal' %}
```

### 5) Troubleshooting

- If a modal does not open, confirm `modals.js` and `modals.css` are loaded on the page.
- If modal AJAX calls fail, verify CSRF middleware/token setup.
- If nested modals behave unexpectedly, check custom JS handlers for Bootstrap modal events.

See `django_examples` for full working examples.
