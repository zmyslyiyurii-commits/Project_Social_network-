import os
from datetime import timedelta
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, Http404
from django.db.models import Max, Q
from django.urls import reverse_lazy
from django.utils import timezone

from users.models import Snap, Story, StoryView
from .forms import StoryForm


class OpenHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'openhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # 1. Знаходимо ID найновішого снапа для кожного унікального відправника
        latest_snap_ids = (
            Snap.objects.filter(receiver=user)
            .values('sender')
            .annotate(latest_id=Max('id'))
            .values_list('latest_id', flat=True)
        )

        # 2. Отримуємо снапи по цих ID та сортуємо за датою
        snaps = (
            Snap.objects.filter(id__in=latest_snap_ids)
            .select_related('sender', 'sender__profile')
            .order_by('-created_at')
        )

        # 3. Знаходимо ID історій, які ПОТОЧНИЙ користувач вже переглянув
        viewed_story_ids = StoryView.objects.filter(
            user=user
        ).values_list('story_id', flat=True)

        # 4. Знаходимо ID користувачів, які мають АКТИВНІ та ЩЕ НЕ ПЕРЕГЛЯНУТІ історії
        cutoff_time = timezone.now() - timedelta(hours=24)
        active_story_user_ids = set(
            Story.objects.filter(created_at__gte=cutoff_time)
            .exclude(id__in=viewed_story_ids)
            .values_list('user_id', flat=True)
        )

        # 5. Передаємо прапорець `has_active_story` кожному відправнику
        for snap in snaps:
            snap.sender.has_active_story = snap.sender.id in active_story_user_ids

        context['snaps'] = snaps
        return context


class SnapDetailView(LoginRequiredMixin, DetailView):
    model = Snap
    template_name = 'snap_detail.html'
    context_object_name = 'snap'

    def get_queryset(self):
        return Snap.objects.filter(
            Q(receiver=self.request.user) | Q(sender=self.request.user)
        )

    def get_object(self, queryset=None):
        snap = super().get_object(queryset)

        if snap.status == 'opened' and self.request.user == snap.receiver:
            raise PermissionError("Цей снап уже був переглянутий.")

        if snap.status == 'sent' and self.request.user == snap.receiver:
            snap.status = 'opened'
            snap.save(update_fields=['status'])

        return snap

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except PermissionError:
            return HttpResponseForbidden("Цей снап уже був переглянутий.")


class CreateStoryView(LoginRequiredMixin, CreateView):
    model = Story
    form_class = StoryForm
    template_name = 'create_story.html'
    success_url = reverse_lazy('SnapPage:openhome')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UserStoryDetailView(LoginRequiredMixin, DetailView):
    model = Story
    template_name = 'story_detail.html'
    context_object_name = 'story'

    def get_object(self, queryset=None):
        user_id = self.kwargs.get('user_id')
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        # Отримуємо ID вже переглянутих історій цим користувачем
        viewed_story_ids = StoryView.objects.filter(
            user=self.request.user
        ).values_list('story_id', flat=True)

        # Шукаємо найновішу НЕПЕРЕГЛЯНУТУ історію обраного користувача
        story = Story.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_time
        ).exclude(
            id__in=viewed_story_ids
        ).order_by('-created_at').first()

        # Якщо всі нові переглянуті, показуємо хоча б останню активну історію
        if not story:
            story = Story.objects.filter(
                user_id=user_id,
                created_at__gte=cutoff_time
            ).order_by('-created_at').first()

        if not story:
            raise Http404("Активних історій для цього користувача не знайдено.")

        # Фіксуємо перегляд
        StoryView.objects.get_or_create(story=story, user=self.request.user)
            
        return story