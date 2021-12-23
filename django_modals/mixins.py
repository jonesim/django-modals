from django.template.loader import render_to_string


class ScratchPad:

    def button_scratchpad(self, *, scratchpad):
        if scratchpad == 0:
            return self.command_response(
                'append_to', html=render_to_string('django_modals/scratchpad.html'),
                check_id='scratchpad', selector='body'
            )
        else:
            return self.command_response('null')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['scratchpad'] = True
        return context
