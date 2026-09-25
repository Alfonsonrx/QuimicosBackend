from datetime import time

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class AssistanceRecord(models.Model):
    class AssistanceType(models.TextChoices):
        # actual_value_stored_in_db, human_readable_display_name
        INGRESO = "ingreso", _("ingreso")
        SALIDA = "salida", _("salida")
        FALTA_ANTICIPADA = "falta_anticipada", _("falta anticipada")

    id = models.BigAutoField(_("Record Id"),unique=True, primary_key=True)

    date=models.DateField()
    time=models.TimeField()
    type = models.CharField(
        max_length=16,
        choices=AssistanceType.choices,
        default=AssistanceType.INGRESO,
    )
    delay = models.BooleanField(default=False)
    early_exit = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='assistances', on_delete=models.CASCADE)

    def __str__(self):
        return f'{0} - {1} - {2}'.format(self.user.nickname, self.type, self.timestamp)



class WorkSchedule(models.Model):
    """Company-wide schedule (single row). Flags are computed when a record is marked, so edits here don't rewrite history."""
    entry_time = models.TimeField(default=time(9, 30))
    exit_time = models.TimeField(default=time(17, 30))

    @classmethod
    def get(cls):
        return cls.objects.get_or_create(pk=1)[0]

    def is_late(self, t):
        return t > self.entry_time

    def is_early_exit(self, t):
        return t < self.exit_time


class ReentryPermit(models.Model):
    """Admin authorization for one extra ingreso on a day the user already marked salida."""
    user = models.ForeignKey(User, related_name='reentry_permits', on_delete=models.CASCADE)
    date = models.DateField()
    granted_by = models.ForeignKey(User, related_name='+', null=True, on_delete=models.SET_NULL)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
