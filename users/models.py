import os
import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


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
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('avatars/', filename)


# Динамічна функція для безпечного збереження файлів історій (із запобіганням помилок через кирилицю)
def story_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('stories/', filename)


# Модель профілю з оптимізованим збереженням медіа
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=user_avatar_path, default="avatars/default.png", blank=True)
    snap_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"Профіль користувача {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar and os.path.exists(self.avatar.path) and "default.png" not in self.avatar.name:
            try:
                from PIL import Image
                img = Image.open(self.avatar.path)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception as e:
                print(f"Помилка при обробці зображення: {e}")


class Snap(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Відправлено'),
        ('opened', 'Відкрито'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_snaps')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_snaps')
    media_file = models.FileField(upload_to='snaps/')
    duration = models.IntegerField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Тривалість від 1 до 10 секунд. Залиште порожнім для безлімітного перегляду."
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Снап"
        verbose_name_plural = "Снапи"

    @property
    def is_opened(self):
        """Повертає True, якщо снап було переглянуто."""
        return self.status == 'opened'

    def __str__(self):
        duration_str = f"{self.duration}s" if self.duration else "безлімітно"
        return f"Снап від {self.sender} до {self.receiver} (Час: {duration_str}) - {self.get_status_display()}"


# Модель текстових повідомлень з підтримкою статусу перегляду
class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name="Відправник"
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages',
        verbose_name="Отримувач"
    )
    text = models.TextField(
        verbose_name="Текст повідомлення"
    )
    is_read = models.BooleanField(
        default=False, 
        verbose_name="Статус перегляду"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Час відправки"
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = "Повідомлення"
        verbose_name_plural = "Повідомлення"

    def __str__(self):
        status_str = "Прочитано" if self.is_read else "Не прочитано"
        return f"Від {self.sender.username} до {self.recipient.username} ({status_str})"


class Story(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stories',
        verbose_name="Користувач"
    )
    media_file = models.FileField(
        upload_to=story_file_path,
        verbose_name="Медіафайл"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Час публікації"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Історія"
        verbose_name_plural = "Історії"

    def __str__(self):
        return f"Історія від {self.user.username} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"

    @property
    def is_active(self):
        """Перевіряє, чи історія була опублікована протягом останніх 24 годин."""
        return timezone.now() <= self.created_at + timedelta(hours=24)


# Модель для фіксації переглядів історій
class StoryView(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='story_views')
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('story', 'user')
        verbose_name = "Перегляд історії"
        verbose_name_plural = "Перегляди історій"

    def __str__(self):
        return f"{self.user.username} переглянув історію #{self.story.id}"


class Friendship(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Надіслано запит'),
        ('accepted', 'Прийнято'),
        ('blocked', 'Заблоковано'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_requests_sent')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship_requests_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.get_status_display()})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()