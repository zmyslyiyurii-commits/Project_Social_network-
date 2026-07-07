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
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)