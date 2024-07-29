import base64
import json

import binascii
from ajax_helpers.mixins import AjaxHelpers
from ajax_helpers.utils import is_ajax, ajax_command
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic.base import TemplateView
from django_menus.menu import HtmlMenu, HtmlMenuItem
from html_classes.font_awesome import font_awesome
from html_classes.html import HtmlButton
from django_modals.helper import (render_modal, modal_button, modal_button_group, ajax_modal_redirect,
                                  modal_button_method, ajax_modal_replace)


class ModalException(Exception):
    pass


@method_decorator(ensure_csrf_cookie, name='dispatch')
class BaseModalMixin(AjaxHelpers):
    request: HttpRequest
    kwargs: dict
    button_group_class = None
    button_container_class = None
    menu_config = {'href_format': "javascript:django_modal.show_modal('{}')"}
    ajax_commands = ['button', 'select2', 'ajax']
    button_group_css = None
    size = 'lg'
    no_parent_template = 'django_modals/blank_page_form.html'

    def __init__(self):
        super().__init__()
        if not hasattr(self, 'modal_mode'):
            self.modal_mode = True
        self.top_menu = HtmlMenu(template='django_modals/modal_menu.html')
        if not getattr(self, 'no_header_x', None):
            self.top_menu.add_items(HtmlMenuItem(html=HtmlButton(data_dismiss='modal',
                                                                 contents=font_awesome('fas fa-times'))))
        self.slug = {}

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs) if hasattr(super(), 'get_context_data') else {}
        context.update({'request': self.request, 'slug': self.slug})
        context['modal_url'] = kwargs.get('modal_url', self.request.get_full_path())
        context['center_header'] = kwargs.get('center_header', getattr(self, 'center_header', None))
        context['size'] = kwargs.get('size', self.size)
        context['modal_type'] = self.kwargs.get('modal_type')
        context['header_menu'] = self.top_menu
        return context

    def split_slug(self, kwargs):
        if 'slug' in kwargs and kwargs['slug'] != '-':
            s = kwargs['slug'].split('-')
            if len(s) == 1:
                self.slug['pk'] = s[0]
            else:
                self.slug.update({s[k]: s[k+1] for k in range(0, int(len(s)-1), 2)})
            if 'pk' in self.slug:
                self.kwargs['pk'] = self.slug['pk']

    def process_slug_kwargs(self):
        return True

    def split_base64(self, kwargs):
        if 'base64' in kwargs:
            try:
                base64_data = json.loads(base64.urlsafe_b64decode(self.kwargs['base64']))
            except binascii.Error:
                raise ModalException('Error in modal base64 decode - This modal requires base64 not a slug')
            if not isinstance(base64_data, dict):
                base64_data = {'base64': base64_data}
            self.slug.update(base64_data)
            self.kwargs.update(base64_data)

    def dispatch(self, request, *args, **kwargs):
        self.split_slug(kwargs)
        self.split_base64(kwargs)
        if self.process_slug_kwargs():
            # noinspection PyUnresolvedReferences
            return super().dispatch(request, *args, **self.kwargs)
        else:
            raise ModalException('User does not have permission')

    def button_refresh_modal(self, **_kwargs):
        return self.command_response(ajax_modal_replace(self.request, modal_class=self.__class__,
                                                        slug=self.kwargs.get('slug', '-')))

    def button_group(self):
        button_kwargs = {
            'button_group_class': self.kwargs.get('button_group_class', self.button_group_class),
            'button_container_class': self.kwargs.get('button_container_class', self.button_container_class)
        }
        button_kwargs = {k: v for k, v in button_kwargs.items() if v}
        return modal_button_group(self.buttons, **button_kwargs)

    def check_for_background_page(self, context):
        if not is_ajax(self.request) and self.modal_mode:
            context['modal_type'] = 'no-parent'
            if not getattr(self, 'no_header_x', None):
                del self.top_menu.menu_items[0]
            context['form'] = render_modal(template_name=self.template_name, **context)
            # noinspection PyAttributeOutsideInit
            self.template_name = self.no_parent_template

    def modal_replace(self, modal_name=None, modal_class=None, slug='-', **kwargs):
        return self.command_response(ajax_modal_replace(self.request, modal_name, slug=slug,
                                                        modal_class=modal_class, **kwargs))

    def message(self, message, title=None, **modal_kwargs):
        if title is not None:
            modal_kwargs['modal_title'] = title
        return self.modal_replace(modal_class=Modal, message=message, ajax_function='modal_html', **modal_kwargs)

    def confirm(self, message, title=None, button_group_type='confirm', **kwargs):
        return self.message(message, title=title, button_group_type=button_group_type, **kwargs)

    def modal_redirect(self, modal_name, slug='-'):
        return self.command_response(ajax_modal_redirect(modal_name, slug))


class BaseModal(BaseModalMixin, TemplateView):
    template_name = 'django_modals/modal_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_title'] = kwargs.get('modal_title', getattr(self, 'modal_title', None))
        self.check_for_background_page(context)
        return context


class Modal(BaseModal):

    def modal_content(self):
        return self.kwargs.get('message', '')

    def get_modal_buttons(self):
        if 'buttons' in self.kwargs:
            return self.kwargs['buttons']
        button_group_type = self.kwargs.get('button_group_type')
        if button_group_type == 'confirm':
            return [
                modal_button_method('Confirm', self.kwargs.get('button_function', 'confirm'), 'btn-success'),
                modal_button('Cancel', 'close', 'btn-secondary')
            ]
        elif button_group_type == 'yes_cancel':
            return [
                modal_button_method('Yes', self.kwargs.get('button_function', 'confirm'), 'btn-danger'),
                modal_button('Cancel', 'close', 'btn-success')
            ]
        else:
            return [modal_button('OK', 'close', 'btn-success')]

    @property
    def extra_context(self):
        if not self._extra_content:
            modal_content = self.modal_content()
            if not self.buttons:
                self.buttons = self.get_modal_buttons()

            if self.page_commands:
                command = ajax_command('onload', commands=self.page_commands)
                page_command_script = mark_safe(f'''<script>
                                 $(document).off("modalPostLoad");
                                 $(document).on("modalPostLoad",function(){{
                                    ajax_helpers.process_commands([{json.dumps(command)}]);
                                    $(document).off("modalPostLoad");
                                 }})
                                 </script>''')
            else:
                page_command_script = mark_safe(f'''<script>
                                 $(document).off("modalPostLoad");
                                 </script>''')

            self._extra_content = {'form': mark_safe(modal_content + self.button_group() + page_command_script)}
        return self._extra_content

    def __init__(self):
        if not hasattr(self, 'buttons'):
            self.buttons = []
        self._extra_content = None
        super().__init__()


class TemplateModal(Modal):

    modal_template = None

    def modal_context(self):
        context = self.kwargs.get('context', {})
        return context

    def modal_content(self):
        return render_to_string(self.modal_template, self.modal_context())

    def __init__(self, modal_template=None, modal_title=None, size=None, **kwargs):
        # These kwargs will be overwritten if called as_view()
        self.kwargs = kwargs
        if size:
            self.size = size
        if modal_title:
            self.modal_title = modal_title
        if modal_template:
            self.modal_template = modal_template
        super().__init__()

    def modal_html(self, request):
        self.request = request
        context = self.get_context_data()
        if 'message' in self.kwargs:
            context['message'] = self.kwargs['message']
        return render_to_string(self.template_name, context)

