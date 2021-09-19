from show_src_code.apps import PypiAppConfig


class ModalExampleConfig(PypiAppConfig):
    default = True
    name = 'modal_examples'
    pypi = 'django-nested-modals'
    urls = 'modal_examples.urls'
