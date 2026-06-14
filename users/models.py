from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('email field is required')

        user = self.model(
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, password=None, **extra_fields):
        superuser = self.create_user(
            email=email,
            password=password,
        )
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.is_active = True
        superuser.save(using=self._db)
        return superuser

class UserTag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    name = models.CharField(max_length=30, null=False, blank=False)
    # T : 여자, F : 남자
    gender = models.BooleanField(default=False)
    age = models.IntegerField(default=0, validators=[MinValueValidator(0),])
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(UserTag)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

