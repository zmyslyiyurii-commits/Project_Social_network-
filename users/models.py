from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Тут ми наслідуємо всі стандартні поля (username, email, password...)
    # І можемо одразу або пізніше додавати специфічні поля для Snapchat
    bio = models.TextField(max_length=500, blank=True, verbose_name="Біографія")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")

    def __str__(self):
        return self.username