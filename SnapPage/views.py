from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from users.models import Snap

class OpenHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'openhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Знаходимо ID найновішого снапа для кожного унікального відправника
        latest_snap_ids = (
            Snap.objects.filter(receiver=self.request.user)
            .values('sender')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        #  Отримуємо самі снапи по цих ID та сортуємо за датою
        context['snaps'] = (
            Snap.objects.filter(id__in=latest_snap_ids)
            .select_related('sender')
            .order_by('-created_at')
        )
        return context


class SnapDetailView(LoginRequiredMixin, DetailView):
    model = Snap
    template_name = 'snap_detail.html'
    context_object_name = 'snap'

    def get_queryset(self):
        return Snap.objects.filter(receiver=self.request.user)

    def get_object(self, queryset=None):
        snap = super().get_object(queryset)
        # Якщо снап був 'sent', при відкритті міняємо на 'opened'
        if snap.status == 'sent':
            snap.status = 'opened'
            snap.save(update_fields=['status'])
        return snap