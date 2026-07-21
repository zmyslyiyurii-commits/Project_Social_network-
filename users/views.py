from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views import View
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Міксин для захисту доступу до сторінки
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm  # Кастомні форми
from .models import Profile, User

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