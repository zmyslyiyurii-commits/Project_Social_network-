from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm  # кастомна форма реєстрації

# ФУНКЦІЯ РЕЄСТРАЦІЇ (яку зараз не бачить Django)
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('openhome')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# ФУНКЦІЯ ВХОДУ
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('openhome')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})