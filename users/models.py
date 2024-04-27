from django.contrib.auth.models import AbstractUser
from django.db import models
from jsonfield import JSONField
from uuid import uuid4

class User(AbstractUser):
    photo = models.ImageField(upload_to="users/%Y/%m/%d/", default="users/default.png", blank=True, null=True, verbose_name="Фотография")
    date_birth = models.DateTimeField(blank=True, null=True, verbose_name="Дата рождения")
    completed_quizes = JSONField(null=True, default=[], verbose_name="completed_quizes")
    created_quizes = models.TextField(null=True, default=[], verbose_name="created_quizes")
    email_activated = models.BooleanField(default=False)
    confirm_key = models.TextField(default="")