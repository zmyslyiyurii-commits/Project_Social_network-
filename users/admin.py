from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Friendship, Snap

# Реєструємо нашу кастомну модель із використанням стандартного UserAdmin
admin.site.register(User, UserAdmin)
admin.site.register(Profile)

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('sender__username', 'receiver__username')
    
@admin.register(Snap)
class SnapAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'duration', 'created_at')
    list_filter = ('status', 'created_at')