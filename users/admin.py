from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Реєструємо нашу кастомну модель із використанням стандартного UserAdmin
admin.site.register(User, UserAdmin)
