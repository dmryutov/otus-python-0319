from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    User model
    """
    avatar = models.ImageField(upload_to='user', default='user/no-avatar.png')
