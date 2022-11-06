from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

NULLABLE = {
    'blank': True,
    'null': True
}


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
