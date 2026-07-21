from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Міксин для захисту доступу до сторінки
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm, SendSnapForm  # Кастомні форми
from .models import Profile, User, Snap

# КЛАС РЕЄСТРАЦІЇ 
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('openhome')  # Куди перенаправити після успішної реєстрації

    def form_valid(self, form):
        # Цей метод викликається, коли форма успішно пройшла валідацію
        response = super().form_valid(form)
        # self.object — це користувач, якого Django щойно зберіг у базу
        login(self.request, self.object)
        return response

# КЛАС ВХОДУ 
class CustomLoginView(LoginView):
    template_name = 'login.html'
    # Django автоматично перенаправить користувача після входу на адресу,
    # вказану в LOGIN_REDIRECT_URL у settings.py (або на 'openhome')

# КЛАС СТОРІНКИ ПРОФІЛЮ 
class ProfileView(LoginRequiredMixin, View):
    template_name = 'profile.html'

    def get(self, request):
        # Оскільки юзер авторизований, ми отримуємо або створюємо його профіль
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        # Ініціалізуємо форми поточними даними юзера та його профілю
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

        context = {
            'profile': profile,  # Під цим ім'ям профіль буде доступний у шаблоні profile.html
            'u_form': u_form,
            'p_form': p_form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Передаємо POST-дані та request.FILES для обробки завантаженого аватара
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профіль успішно оновлено!')
            return redirect('profile')

        context = {
            'profile': profile,  # Під цим ім'ям профіль буде доступний у шаблоні profile.html
            'u_form': u_form,
            'p_form': p_form,
        }
        return render(request, self.template_name, context)


# В’Ю ВІДПРАВКИ СНАПУ 
class SendSnapView(LoginRequiredMixin, View):
    template_name = 'send_snap.html'

    def get(self, request, *args, **kwargs):
        form = SendSnapForm(user=request.user)
        
        # Якщо в URL передали ID друга (наприклад /snaps/send/3/), підставляємо його за замовчуванням
        receiver_id = kwargs.get('receiver_id')
        if receiver_id:
            receiver = get_object_or_404(User, id=receiver_id)
            if request.user.is_friend_with(receiver):
                form.initial['receiver'] = receiver

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = SendSnapForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            snap = form.save(commit=False)
            snap.sender = request.user
            
            # Додаткова перевірка підтвердженої дружби
            if not request.user.is_friend_with(snap.receiver):
                messages.error(request, "Ви можете надсилати снапи тільки друзям!")
                return render(request, self.template_name, {'form': form})
            
            snap.save()
            messages.success(request, f"Снап успішно надіслано користувачу {snap.receiver.username}!")
            return redirect('openhome')

        return render(request, self.template_name, {'form': form})


# API В’Ю ВІДПРАВКИ СНАПУ 
class SendSnapAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        receiver_id = request.POST.get('receiver_id')
        media_file = request.FILES.get('media_file')
        duration = request.POST.get('duration')

        if not receiver_id or not media_file:
            return JsonResponse({'error': 'Отримувач та медіа-файл є обов\'язковими'}, status=400)

        receiver = get_object_or_404(User, id=receiver_id)

        # Перевірка дружби
        if not request.user.is_friend_with(receiver):
            return JsonResponse({'error': 'Ви можете надсилати снапи тільки друзям'}, status=403)

        # Валідація тривалості
        try:
            duration = int(duration) if duration else None
            if duration and (duration < 1 or duration > 10):
                return JsonResponse({'error': 'Тривалість має бути від 1 до 10 секунд'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Некоректне значення тривалості'}, status=400)

        # Створення запису в базі
        snap = Snap.objects.create(
            sender=request.user,
            receiver=receiver,
            media_file=media_file,
            duration=duration,
            status='sent'
        )

        return JsonResponse({
            'message': 'Снап успішно відправлено!',
            'snap_id': snap.id,
            'receiver': receiver.username
        }, status=201)