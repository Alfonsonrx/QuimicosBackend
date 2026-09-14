from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserAccManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        # actual_value_stored_in_db, human_readable_display_name
        EMPLEADO = "empleado", _("empleado")
        ADMIN = "administrador", _("administrador")

    id = models.BigAutoField(_("User Id"),unique=True, primary_key=True)
    nickname = models.CharField(_("Nickname"),max_length=64, unique=True)

    name=models.CharField(max_length=100)
    first_lastname=models.CharField(max_length=100)
    second_lastname=models.CharField(max_length=100, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(null=True, default=False)

    is_active = models.BooleanField(null=True, default=True)
    type = models.CharField(
        max_length=16,
        choices=UserType.choices,
        default=UserType.EMPLEADO,
    )
    phone = models.CharField(max_length=100, null=True, blank=True)

    date_registered = models.DateTimeField(auto_now_add=True)

    objects = UserAccManager()

    USERNAME_FIELD = 'nickname'
    REQUIRED_FIELDS = ['name', 'first_lastname']
    def __str__(self):
        return f'{0} - {1}'.format(self.name, self.first_lastname)
