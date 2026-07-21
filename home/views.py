from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from users.models import Snap  

class HomeView(TemplateView):
    template_name = 'home.html'

class OpenHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'openhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # Снапи, які НАДІСЛАЛИ поточному користувачу (Отримувач)
        context['received_snaps'] = Snap.objects.filter(receiver=user).select_related('sender')
        # Снапи, які користувач НАДІСЛАВ сам (Відправник)
        context['sent_snaps'] = Snap.objects.filter(sender=user).select_related('receiver')
        return context