from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Міксин для захисту доступу до сторінки
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm  #  кастомна форма реєстрації
from .models import Profile

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
class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'  # Під цим ім'ям профіль буде доступний у шаблоні profile.html

    def get_object(self, queryset=None):
        # Оскільки юзер авторизований, ми отримуємо або створюємо його профіль
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile