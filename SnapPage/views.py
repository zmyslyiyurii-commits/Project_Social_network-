import os
from datetime import datetime, timedelta, timezone as py_timezone
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.db.models import Max, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from users.models import Snap, Story, StoryView, Friendship
from .forms import StoryForm, SnapForm

User = get_user_model()


class OpenHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'openhome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        friends = user.get_friends()

        cutoff_time = timezone.now() - timedelta(hours=24)
        viewed_story_ids = set(
            StoryView.objects.filter(user=user).values_list('story_id', flat=True)
        )
        active_story_user_ids = set(
            Story.objects.filter(created_at__gte=cutoff_time)
            .exclude(id__in=viewed_story_ids)
            .values_list('user_id', flat=True)
        )

        chats = []
        for friend in friends:
            latest_snap = Snap.objects.filter(
                (Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user))
            ).order_by('-created_at').first()

            chats.append({
                'friend': friend,
                'latest_snap': latest_snap,
                'has_active_story': friend.id in active_story_user_ids
            })

        chats.sort(
            key=lambda c: c['latest_snap'].created_at if c['latest_snap'] else datetime.min.replace(tzinfo=py_timezone.utc),
            reverse=True
        )

        pending_requests_count = Friendship.objects.filter(
            receiver=user, 
            status='sent'
        ).count()

        context['chats'] = chats
        context['friends'] = friends
        context['snap_form'] = SnapForm(user=user)
        context['story_form'] = StoryForm()
        context['pending_requests_count'] = pending_requests_count
        return context


class AddFriendsPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'add_friends_panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        query = self.request.GET.get('q', '').strip()

        pending_requests = Friendship.objects.filter(
            receiver=user, 
            status='sent'
        ).select_related('sender', 'sender__profile')

        accepted_friendships = Friendship.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status='accepted'
        )
        accepted_friend_ids = set()
        for f in accepted_friendships:
            accepted_friend_ids.add(f.sender_id)
            accepted_friend_ids.add(f.receiver_id)

        incoming_ids = set(pending_requests.values_list('sender_id', flat=True))
        excluded_ids = {user.id} | accepted_friend_ids | incoming_ids

        users_qs = User.objects.exclude(id__in=excluded_ids).select_related('profile')
        if query:
            users_list = users_qs.filter(username__icontains=query).order_by('-date_joined')
        else:
            users_list = users_qs.order_by('-date_joined')[:50]

        sent_request_user_ids = set(
            Friendship.objects.filter(sender=user, status='sent').values_list('receiver_id', flat=True)
        )

        context['pending_requests'] = pending_requests
        context['suggested_users'] = users_list
        context['sent_request_user_ids'] = sent_request_user_ids
        context['query'] = query
        return context


@require_POST
def send_friend_request(request, user_id):
    """Надіслати запит на додавання в друзі"""
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        return JsonResponse({'status': 'error', 'message': 'Неможливо додати самого себе'}, status=400)

    friendship, created = Friendship.objects.get_or_create(
        sender=request.user,
        receiver=target_user,
        defaults={'status': 'sent'}
    )
    if not created and friendship.status != 'sent':
        friendship.status = 'sent'
        friendship.save()

    return JsonResponse({'status': 'success', 'message': 'Запит надіслано'})


@require_POST
def accept_friend_request(request, request_id):
    """Прийняти вхідний запит у друзі"""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user)
    friendship.status = 'accepted'
    friendship.save()

    # Отримуємо нового друга
    friend = friendship.sender
    avatar_url = friend.profile.avatar.url if hasattr(friend, 'profile') and friend.profile.avatar else ''

    # Перераховуємо залишок запитів
    remaining_requests_count = Friendship.objects.filter(
        receiver=request.user, 
        status='sent'
    ).count()

    return JsonResponse({
        'status': 'success',
        'message': 'Запит прийнято',
        'request_id': request_id,
        'remaining_count': remaining_requests_count,
        'friend': {
            'id': friend.id,
            'username': friend.username,
            'avatar_url': avatar_url,
        }
    })


@require_POST
def reject_friend_request(request, request_id):
    """Відхилити/видалити запит у друзі"""
    friendship = get_object_or_404(Friendship, id=request_id, receiver=request.user)
    friendship.delete()

    remaining_requests_count = Friendship.objects.filter(
        receiver=request.user, 
        status='sent'
    ).count()

    return JsonResponse({
        'status': 'success', 
        'message': 'Запит скасовано',
        'request_id': request_id,
        'remaining_count': remaining_requests_count
    })


# ==========================================
# РЕШТА В'ЮШОК (СНАПИ ТА ІСТОРІЇ)
# ==========================================

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
            raise PermissionDenied("Цей снап уже був переглянутий.")

        if snap.status == 'sent' and self.request.user == snap.receiver:
            snap.status = 'opened'
            snap.save(update_fields=['status'])

        return snap


class CreateSnapView(LoginRequiredMixin, CreateView):
    model = Snap
    form_class = SnapForm
    success_url = reverse_lazy('SnapPage:openhome')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)


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

        viewed_story_ids = StoryView.objects.filter(
            user=self.request.user
        ).values_list('story_id', flat=True)

        story = Story.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_time
        ).exclude(
            id__in=viewed_story_ids
        ).order_by('-created_at').first()

        if not story:
            story = Story.objects.filter(
                user_id=user_id,
                created_at__gte=cutoff_time
            ).order_by('-created_at').first()

        if not story:
            raise Http404("Активних історій для цього користувача не знайдено.")

        StoryView.objects.get_or_create(story=story, user=self.request.user)

        return story