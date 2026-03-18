from .views import MainMenuTemplateView


class HelpView(MainMenuTemplateView):
    template_name = 'example_views/help.html'
