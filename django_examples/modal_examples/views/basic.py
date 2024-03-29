from django_menus.menu import AjaxButtonMenuItem
from show_src_code.modals import Modal, TemplateModal

from django_modals.decorators import ConfirmAjaxMethod, ConfirmYesNoCancelAjaxMethod
from django_modals.helper import modal_button, modal_button_method, ajax_modal_redirect
from django_modals.url_helper import get_urls
from .views import MainMenuTemplateView


class Basic(MainMenuTemplateView):

    template_name = 'example_views/basic.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('hello_modal', 'Simple Message'),
            ('hello_title_modal', 'Message with title'),
            ('ModalConfirm,-', 'Confirm'),
            'forward_example,-'
        )
        self.add_menu('template', 'buttons', ).add_items(
            ('template_modal,-', 'Template Modal'),
            ('template_modal_ajax,-', 'Template Modal with ajax button'),
            ('TemplateModalButtons,-', 'Template Modal with ajax button'),
        )

        self.add_menu('confirm', 'buttons', ).add_items(
            AjaxButtonMenuItem(button_name='confirm',
                               menu_display='Confirm ajax method'),
            AjaxButtonMenuItem(button_name='yes_or_no',
                               menu_display='Yes or No ajax method')
        )

    @ConfirmAjaxMethod(message="Would you like to confirm?")
    def button_confirm(self, **_kwargs):
        return self.command_response('message', text='confirmed')

    @ConfirmYesNoCancelAjaxMethod(message="Press yes or no?")
    def button_yes_or_no(self, **_kwargs):
        if _kwargs['confirm']:
            return self.command_response('message', text='yes')
        else:
            return self.command_response('message', text='no')


class ModalConfirm(Modal):

    def modal_content(self):
        return 'Custom buttons with confirm stacked modal'

    def get_modal_buttons(self):
        return [modal_button_method('Confirm', 'confirm_message', font_awesome='fas fa-check'),
                modal_button('Cancel', 'close', 'btn-secondary', font_awesome='fas fa-times')]

    def button_confirm_message(self, **_kwargs):
        return self.confirm('Confirm message - Confirming will execute button_confirm method')

    def button_confirm(self, **_kwargs):
        self.add_command('close')
        self.add_command('message', text='closed confirm modal - now close original modal')
        return self.command_response('close')


class HelloModal(Modal):
    button_container_class = 'text-center'

    def modal_content(self):
        return 'Hello<br>Message no title default OK button '


class HelloTitleModal(Modal):
    button_container_class = 'text-center'
    modal_title = ' Modal Title'

    def modal_content(self):
        return 'Hello<br>Message with title default OK button '


class TemplateModalExample(TemplateModal):

    modal_template = 'modal_examples/modal_template.html'

    def modal_context(self):
        return {'view': 'From view'}


class TemplateModalAjax(TemplateModal):

    modal_template = 'modal_examples/modal_template_ajax.html'

    def modal_context(self):
        return {'view': 'From view'}

    def button_ajax_command(self, **_kwargs):
        return self.command_response('message', text='Ajax button pressed')


class TemplateModalButtons(TemplateModal):

    modal_template = 'modal_examples/modal_template.html'
    buttons = [modal_button('Custom Close', 'close', 'btn-warning')]

    def modal_context(self):
        return {'view': 'From view'}


class ConfirmModal(Modal):

    def get_modal_buttons(self):
        return [modal_button('Yes', {'function': 'post_modal', 'button': 'confirm_yes'}, 'btn-success')]

    def modal_content(self):
        return self.kwargs.get('message', 'Are you sure?')


class ForwardingExample(Modal):
    button_group_class = 'pl-1'
    modal_title = 'Forwarding Example'

    def get_modal_buttons(self):
        return [modal_button_method('Replace', 'replace', 'btn-success'),
                modal_button_method('Redirect', 'redirect', 'btn-success mx-1'),
                modal_button_method('Confirm', 'confirm_message', 'btn-success mx-1'),
                modal_button_method('Message', 'message', 'btn-warning mx-1')]

    def button_message(self, **_kwargs):
        return self.message('Message modal on top of calling modal', 'Message Title',
                            button_container_class='text-center')

    def button_redirect(self, **_kwargs):
        return self.modal_redirect('forward_example1')

    def button_replace(self, **_kwargs):
        return self.modal_replace('forward_example2')

    def button_confirm(self, **_kwargs):
        self.add_command('close')
        return self.command_response('message', text='Confirmed')

    def button_confirm_message(self, **_kwargs):
        return self.confirm('Confirm Message', 'Confirm Title')

    def button_confirm_yes(self, **_kwargs):
        return self.command_response('close')


class ForwardingExample1(Modal):

    modal_title = 'Forwarding Example - Redirect'

    def get_modal_buttons(self):
        return [
            modal_button('Close', 'close', 'btn-danger'),
            modal_button('Back', ajax_modal_redirect('forward_example'), 'btn-success')]

    def modal_content(self):
        return 'Forward by redirect'


class ForwardingExample2(Modal):

    modal_title = 'Forwarding Example - Replace'

    def modal_content(self):
        return 'Forward by replace'

    def get_modal_buttons(self):
        return [
            modal_button('Close', 'close', 'btn-danger'),
            modal_button('Back', ajax_modal_redirect('forward_example'), 'btn-success')]


urlpatterns = get_urls(__name__)
