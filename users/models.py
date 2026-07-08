from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    # Тут ми наслідуємо всі стандартні поля (username, email, password...)
    # І можемо одразу або пізніше додавати специфічні поля для Snapchat
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

#  модель профілю 
class Profile(models.Model):
    # Зв'язок "один до одного" з кастомним юзером
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Аватар користувача (завантажується в папку avatars/)
    avatar = models.ImageField(upload_to="avatars/", default="avatars/default.png", blank=True)
    # Унікальний Snapchat-код (генерується автоматично)
    snap_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"Профіль користувача {self.user.username}"
    
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
        # Створюємо унікальний індекс, щоб один юзер не міг надіслати кілька дублюючих запитів одному й тому самому користувачу
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.get_status_display()})"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Використовуємо hasattr для безпечної перевірки наявності профілю
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        # Якщо профілю немає створюємо його
        Profile.objects.create(user=instance)