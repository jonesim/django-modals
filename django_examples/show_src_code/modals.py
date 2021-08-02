import django_modals.view_mixins as view_mixins
from django.utils.safestring import mark_safe

from django_modals.helper import modal_button
from django_modals.view_mixins import SimpleModal
from .source_code import template_source, html_code


class BaseSourceCodeModal(SimpleModal):
    size = 'xl'
    modal_title = 'Source Code'
    code = {'template_src': 'crud'}

    def modal_content(self):
        if self.slug['pk'] not in self.code:
            return template_source(self.slug['template'].replace(':', '/'), self.slug['pk'])
        else:
            code = self.code[self.slug['pk']]
            if callable(code):
                return html_code(code)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['script'] = mark_safe('hljs.highlightAll();')
        return context


class CodeMixin:

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['footer'] = mark_safe('''<div class="p-1" style="text-align:right;background-color:#efefef">
            <button class='btn btn-sm btn-outline-secondary' onclick='django_modal.send_inputs({"button": "code"})'>
            <i class="fab fa-python"></i> Source Code</button></div>''')
        return context

    def button_code(self, **_kwargs):
        code = ''
        try:
            if hasattr(self, 'form_class'):
                code = html_code(self.form_class)
        except OSError:
            pass
        code += html_code(self.__class__)
        # noinspection PyUnresolvedReferences
        return self.modal_render(contents=mark_safe(code), size='xl', header='Source Code',
                                 script=mark_safe('hljs.highlightAll();'), modal_buttons=modal_button('OK', 'close'))


class BootstrapModalMixin(CodeMixin, view_mixins.BootstrapModalMixin):
    pass


class BootstrapModelModalMixin(CodeMixin, view_mixins.BootstrapModelModalMixin):
    pass


class MultiFormView(CodeMixin, view_mixins.MultiFormView):
    pass


class BaseModal(CodeMixin, view_mixins.BaseModal):
    pass


class SimpleModal(CodeMixin, view_mixins.SimpleModal):
    pass


class SimpleModalTemplate(CodeMixin, view_mixins.SimpleModalTemplate):
    pass
