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
    user = models.ForeignKey(User, related_name='assistances', on_delete=models.CASCADE)

    def __str__(self):
        return f'{0} - {1} - {2}'.format(self.user.nickname, self.type, self.timestamp)
