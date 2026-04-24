# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

This is **django-nested-modals**, a Django library providing Bootstrap nested modal dialogs. The repo contains two main parts:

- `django_modals/` — the reusable Django app (the library)
- `django_examples/` — a demo Django project showcasing the library

### Running the dev server

```bash
export PYTHONPATH="/workspace:$PYTHONPATH"
cd /workspace/django_examples
python3 manage.py runserver 0.0.0.0:8007
```

The `PYTHONPATH` must include `/workspace` so the local `django_modals` package is used instead of the pip-installed one. The dev server runs on port **8007**.

### Database

SQLite is used (`django_examples/db.sqlite3`). Run `python3 manage.py migrate` before first use.

To load demo data: `python3 manage.py import_modal_data`

To create a superuser: `python3 manage.py createsuperuser`

### Lint / Tests

Django system checks: `python3 manage.py check` (no separate lint config).

**Playwright test suite** (86 tests in `tests/`):

```bash
# Start the dev server first (in background), then:
cd /workspace
python3 -m pytest tests/ --browser chromium -v
```

The tests require the Django dev server running on `localhost:8007`. Key test helpers are in `tests/helpers.py` — they handle the `ajax_helpers.ajax_busy` timing issue with Bootstrap modal animations.

### Optional services (Celery + Redis)

The Tasks page requires Redis + Celery. These are optional and only needed for async task/progress-bar modal demos. See `docker-compose.yaml` for the Docker-based setup.

### Gotchas

- `pip install -r requirements.txt` also installs `django-nested-modals` from PyPI. The local version in `django_modals/` takes precedence only when `PYTHONPATH` includes the repo root.
- `ALLOWED_HOSTS` is empty in settings, which is fine for `DEBUG=True` (localhost access only).
- The `manage.py` commands must be run from `django_examples/` directory.
