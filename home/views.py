from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

class OpenHomeView(TemplateView):
    template_name = 'openhome.html'