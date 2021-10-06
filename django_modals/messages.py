from .modals import TemplateModal


class AjaxMessagesMixin:
    def warning_message(self, message, title='Warning', **kwargs):
        return self.ajax_message(message, title, icon='<i class="fas fa-exclamation-triangle fa-2x"></i>',
                                 icon_class='text-warning', **kwargs)

    def error_message(self, message, title='Error', **kwargs):
        return self.ajax_message(message, title, icon='<i class="fas fa-exclamation-circle fa-2x"></i>',
                                 icon_class='text-danger', **kwargs)

    def ajax_message(self, message, title='Information',
                     icon='<i class="fas fa-info-circle fa-2x"></i>',
                     icon_class='text-primary',
                     button_container_class='text-center', **kwargs):
        if 'size' not in kwargs:
            if len(message) > 60:
                kwargs['size'] = 'lg'
            elif len(message) > 22:
                kwargs['size'] = 'md'
            else:
                kwargs['size'] = 'sm'
        return self.command_response('modal_html', html=TemplateModal(
            modal_template='django_modals/message.html',
            modal_title=title,
            button_container_class=button_container_class,
            context={'message': message, 'icon': icon, 'icon_class': icon_class}, **kwargs,
        ).modal_html(self.request))
