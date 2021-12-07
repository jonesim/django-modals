from ajax_helpers.html_include import SourceBase, pip_version

version = pip_version('django-nested-modals')


class DefaultInclude(SourceBase):
    static_path = 'ajax_helpers/'
    js_filename = 'ajax_helpers.js'
    js_path = ''


class Modals(SourceBase):
    static_path = 'django_modals/'
    filename = 'modals'
    legacy_js = 'modals_legacy.js'


class Toggle(SourceBase):
    static_path = 'django_modals/'
    cdn_path = 'cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/'
    filename = 'bootstrap4-toggle.min'


class Select2(SourceBase):
    static_path = 'django_modals/'
    cdn_path = 'cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/'
    filename = 'select2.min'


class Select2Widget(SourceBase):
    static_path = 'django_modals/'
    js_filename = 'widget_select2.js'


class JQueryUI(SourceBase):
    static_path = 'django_modals/jquery_ui_limited/'
    filename = 'jquery-ui.min'


class TinyMce(SourceBase):
    static_path = 'django_modals/tinymce/'
    js_filename = 'tinymce.min.js'
    js_path = ''


class ColourPicker(SourceBase):
    static_path = 'django_modals/bootstrap-colorpicker/'
    filename = 'bootstrap-colorpicker'


packages = {
    'select2': [Select2, Select2Widget],
}
