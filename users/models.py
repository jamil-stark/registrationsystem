from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.mail import send_mail
from django.db.models import Max
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, ".env"))


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, name, password, **extra_fields)


class CustomUser(AbstractBaseUser,PermissionsMixin):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            prefix = 'AASC'
            highest_id = CustomUser.objects.aggregate(Max('id'))['id__max']
            if highest_id:
                highest_id_number = int(highest_id.replace(prefix, ''))
                new_id_number = highest_id_number + 1
            else:
                new_id_number = 1
            self.id = f'{prefix}{new_id_number:07}' 
        super(CustomUser, self).save(*args, **kwargs)

        send_mail(
            'User Registration',
            f'Hello {self.name},\n\nYour account has been created successfully.\n\nUsername: {self.username}\nPassword: {self.password}\n\nThank you!',
            os.getenv('EMAIL_HOST_USER'),
            [self.email],
            fail_silently=False,
        )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name']

    objects = CustomUserManager()

    def __str__(self):
        return self.username