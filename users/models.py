import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    # Тут ми наслідуємо всі стандартні поля (username, email, password...)
    bio = models.TextField(max_length=500, blank=True, verbose_name="Біографія")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    
    def is_friend_with(self, other_user):
        # Перевіряє, чи є користувачі підтвердженими друзями
        return Friendship.objects.filter(
            (models.Q(sender=self, receiver=other_user) | models.Q(sender=other_user, receiver=self)),
            status='accepted'
        ).exists()

    def get_friends(self):
        # Повертає список усіх підтверджених друзів користувача
        sent = Friendship.objects.filter(sender=self, status='accepted').values_list('receiver', flat=True)
        received = Friendship.objects.filter(receiver=self, status='accepted').values_list('sender', flat=True)
        friend_ids = list(sent) + list(received)
        return User.objects.filter(id__in=friend_ids)


# Динамічна функція для створення унікальної назви файлу аватара
def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.snap_code}.{ext}"
    return os.path.join('avatars/', filename)


# Модель профілю з оптимізованим збереженням медіа
class Profile(models.Model):
    # Зв'язок "один до одного" з кастомним юзером
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Аватар користувача з кастомним upload_to
    avatar = models.ImageField(upload_to=user_avatar_path, default="avatars/default.png", blank=True)
    # Унікальний Snapchat-код (генерується автоматично)
    snap_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"Профіль користувача {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Стискаємо та форматуємо аватарку через Pillow
        if self.avatar and os.path.exists(self.avatar.path) and "default.png" not in self.avatar.name:
            try:
                from PIL import Image
                img = Image.open(self.avatar.path)

                # Зменшуємо картинку до фіксованого розміру 300x300 якщо вона більша
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                print(f"Помилка при обробці зображення: {e}")


class Snap(models.Model):
    # Налаштовуємо варіанти статусів
    STATUS_CHOICES = [
        ('sent', 'Відправлено'),
        ('opened', 'Відкрито'),
    ]
    # Відправник та отримувач
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_snaps')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_snaps')
    # Медіа-файл (завантажується в окрему папку 'snaps/')
    media_file = models.FileField(upload_to='snaps/')
    # Тривалість перегляду: від 1 до 10 секунд, або null (None) для значення "безлімітно"
    duration = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Тривалість від 1 до 10 секунд. Залиште порожнім для безлімітного перегляду."
    )
    # Статус снапу (за замовчуванням — відправлено)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    # Час створення
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # Нові снапи будуть зверху
        verbose_name = "Снап"
        verbose_name_plural = "Снапи"

    def __str__(self):
        duration_str = f"{self.duration}s" if self.duration else "безлімітно"
        return f"Снап від {self.sender} до {self.receiver} (Час: {duration_str}) - {self.get_status_display()}"


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Надіслано запит'),
        ('accepted', 'Прийнято'),
        ('blocked', 'Заблоковано'),
    ]
    # Хто надсилає запит
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_requests_sent')
    # Кому надсилають запит
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_requests_received')
    # Статус дружби
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Унікальний індекс для запобігання дублікатам
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.get_status_display()})"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)