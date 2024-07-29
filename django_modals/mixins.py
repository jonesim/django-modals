from django.template.loader import render_to_string
from django_menus.menu import HtmlMenuItem
from html_classes.font_awesome import font_awesome
from html_classes.html import HtmlButton

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
        self.top_menu.add_items(HtmlMenuItem(html=HtmlButton(
            onclick="ajax_helpers.post_json({url:django_modal.modal_div().attr('data-url')"
                    ", data:{button:'scratchpad', scratchpad:$('#scratchpad').length}})",
            title='Scratch Pad', contents=font_awesome('far fa-sticky-note')))
        )
        context = super().get_context_data(**kwargs)
        return context
