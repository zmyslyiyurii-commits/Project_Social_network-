from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Friendship, Snap


# Вбудовуємо Профіль прямо у сторінку Користувача в адмінці
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профіль користувача (Snapchat)'
    readonly_fields = ('snap_code',)


# Кастомізуємо UserAdmin, щоб бачити bio, birth_date та профіль
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'birth_date', 'is_staff', 'is_superuser')
    # Додаємо наші поля з моделі User у форму редагування
    fieldsets = UserAdmin.fieldsets + (
        ('Snapchat Інформація', {'fields': ('bio', 'birth_date')}),
    )


# Окрема реєстрація моделі Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'snap_code', 'avatar')
    readonly_fields = ('snap_code',)
    search_fields = ('user__username', 'snap_code')


# Адмінка для дружби
@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')


# Адмінка для снапів (з виведенням медіа-файлу)
@admin.register(Snap)
class SnapAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'duration', 'media_file', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'receiver__username')