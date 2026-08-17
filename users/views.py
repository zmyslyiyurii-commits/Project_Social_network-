import json
from itertools import chain
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Міксин для захисту доступу до сторінки
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm  # Кастомні форми
from .models import Profile, User, Message
from .models import Snap

# КЛАС РЕЄСТРАЦІЇ 
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('SnapPage:openhome')  # Куди перенаправити після успішної реєстрації

    def form_valid(self, form):
        # Цей метод викликається, коли форма успішно пройшла валідацію
        response = super().form_valid(form)
        # self.object — це користувач, якого Django щойно зберіг у базу
        login(self.request, self.object)
        return response


# КЛАС ВХОДУ 
class CustomLoginView(LoginView):
    template_name = 'login.html'


# КЛАС СТОРІНКИ ПРОФІЛЮ 
class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

        context = {
            'profile': profile,
            'u_form': u_form,
            'p_form': p_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)

        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профіль успішно оновлено!')
            return redirect('profile')

        context = {
            'profile': profile,
            'u_form': u_form,
            'p_form': p_form,
        }
        return render(request, self.template_name, context)


# ================= ВІДОБРАЖЕННЯ ТА ОБРОБКА ЧАТУ =================
@login_required
def chat_detail(request, friend_id):
    """Відображення вікна чату (повідомлення + снапи) та надсилання повідомлень."""
    friend = get_object_or_404(User, id=friend_id)

    # Обробка надсилання нового повідомлення з чату
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                sender=request.user,
                recipient=friend,
                text=text
            )

    # 1. Отримання текстових повідомлень
    messages_qs = Message.objects.filter(
        (Q(sender=request.user, recipient=friend) | 
         Q(sender=friend, recipient=request.user))
    )

    # 2. Отримання снапів між користувачами
    snaps_qs = Snap.objects.filter(
        (Q(sender=request.user, receiver=friend) | 
         Q(sender=friend, receiver=request.user))
    )

    # 3. Автоматично позначаємо всі отримані повідомлення від цього друга як прочитані
    Message.objects.filter(
        sender=friend,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    # 4. Об'єднуємо повідомлення та снапи, сортуємо за датою створення
    chat_items = sorted(
        chain(messages_qs, snaps_qs),
        key=lambda item: item.created_at
    )

    context = {
        'friend': friend,
        'chat_items': chat_items,
    }
    return render(request, 'chat_detail.html', context)


# ФУНКЦІЇ ДЛЯ РОБОТИ З ПОВІДОМЛЕННЯМИ (API / JSON)
@login_required
@require_POST
def send_message(request, recipient_id):
    """Надсилання текстового повідомлення конкретному користувачу (JSON API)."""
    recipient = get_object_or_404(User, id=recipient_id)
    
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Некоректний JSON'}, status=400)

    if not text:
        return JsonResponse({'status': 'error', 'message': 'Повідомлення не може бути порожнім'}, status=400)

    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        text=text
    )

    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'text': message.text,
            'sender_id': message.sender.id,
            'recipient_id': message.recipient.id,
            'is_read': message.is_read,
            'created_at': message.created_at.strftime('%H:%M')
        }
    })


@login_required
@require_GET
def get_messages(request, user_id):
    """Отримання історії листування з конкретним користувачем (JSON API)."""
    other_user = get_object_or_404(User, id=user_id)
    
    messages_qs = Message.objects.filter(
        (Q(sender=request.user, recipient=other_user) | 
         Q(sender=other_user, recipient=request.user))
    ).order_by('created_at')

    # Позначаємо всі непрочитані повідомлення від цього співрозмовника як прочитані
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    messages_data = [
        {
            'id': msg.id,
            'text': msg.text,
            'sender_id': msg.sender.id,
            'is_me': msg.sender == request.user,
            'is_read': msg.is_read,
            'created_at': msg.created_at.strftime('%H:%M')
        }
        for msg in messages_qs
    ]

    return JsonResponse({'status': 'success', 'messages': messages_data})


@login_required
@require_POST
def mark_messages_as_read(request, sender_id):
    """Позначити всі повідомлення від відправника як прочитані."""
    updated_count = Message.objects.filter(
        sender_id=sender_id,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return JsonResponse({'status': 'success', 'updated_count': updated_count})