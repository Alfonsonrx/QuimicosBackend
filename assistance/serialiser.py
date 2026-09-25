from django.db import transaction
from rest_framework import serializers

from .models import *
from accounts.permissions import is_admin_type

AssistanceType = AssistanceRecord.AssistanceType


def schedule_flags(user, day, record_type, t, exclude_pk=None):
    """delay only on the day's first ingreso; early_exit on any salida before the schedule's exit."""
    schedule = WorkSchedule.get()
    earlier_ingreso = AssistanceRecord.objects.filter(
        user=user, date=day, type=AssistanceType.INGRESO, time__lt=t
    ).exclude(pk=exclude_pk).exists()
    return {
        "delay": record_type == AssistanceType.INGRESO and not earlier_ingreso and schedule.is_late(t),
        "early_exit": record_type == AssistanceType.SALIDA and schedule.is_early_exit(t),
    }

class AssistanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.full_name", read_only=True)
    position = serializers.CharField(source="user.position", read_only=True)

    class Meta:
        model = AssistanceRecord

        fields = [
            "id",
            "date",
            "time",
            "type",
            "user",
            "name",
            "position",
            "delay",
            "early_exit",
        ]
        read_only_fields = ["id", "delay", "early_exit"]

    def validate(self, data):
        record_type = data.get("type", getattr(self.instance, "type", None))
        if record_type == AssistanceRecord.AssistanceType.FALTA_ANTICIPADA:
            request = self.context.get("request")
            if not is_admin_type(getattr(request, "user", None)):
                raise serializers.ValidationError(
                    {"type": "Only administrador-type users can register an anticipated absence."}
                )
        return data

    def create(self, validated_data):
        user, day = validated_data["user"], validated_data["date"]
        record_type = validated_data.get("type", AssistanceType.INGRESO)
        with transaction.atomic():
            # Lock the user row so concurrent marks for the same person are serialized
            User.objects.select_for_update().get(pk=user.pk)
            day_records = AssistanceRecord.objects.filter(user=user, date=day)
            permit = None

            if record_type == AssistanceType.FALTA_ANTICIPADA:
                if day_records.filter(type=AssistanceType.FALTA_ANTICIPADA).exists():
                    raise serializers.ValidationError({"type": ["An anticipated absence already exists for this user on this date."]})
            else:
                last = day_records.exclude(type=AssistanceType.FALTA_ANTICIPADA).order_by("time", "id").last()
                last_type = last.type if last else None
                if record_type == AssistanceType.INGRESO:
                    if last_type == AssistanceType.INGRESO:
                        raise serializers.ValidationError({"type": ["An ingreso is already open for this user on this date."]})
                    if last_type == AssistanceType.SALIDA:
                        permit = ReentryPermit.objects.filter(user=user, date=day, used=False).first()
                        if permit is None:
                            raise serializers.ValidationError({"type": ["Re-entry requires an administrador authorization."]})
                elif last_type != AssistanceType.INGRESO:
                    raise serializers.ValidationError({"type": ["There is no open ingreso to close with a salida."]})

            validated_data.update(schedule_flags(user, day, record_type, validated_data["time"]))
            record = super().create(validated_data)
            if permit:
                permit.used = True
                permit.save(update_fields=["used"])
        return record

    def update(self, instance, validated_data):
        # Corrections skip the marking rules but keep flags consistent with the current schedule
        validated_data.update(schedule_flags(
            validated_data.get("user", instance.user),
            validated_data.get("date", instance.date),
            validated_data.get("type", instance.type),
            validated_data.get("time", instance.time),
            exclude_pk=instance.pk,
        ))
        return super().update(instance, validated_data)


class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = ["entry_time", "exit_time"]

    def validate(self, data):
        entry = data.get("entry_time", self.instance.entry_time)
        exit_ = data.get("exit_time", self.instance.exit_time)
        if entry >= exit_:
            raise serializers.ValidationError({"exit_time": ["exit_time must be later than entry_time."]})
        return data

class TodayCountsSerializer(serializers.Serializer):
    present = serializers.IntegerField()
    absence = serializers.IntegerField()
    anticipated_absence = serializers.IntegerField()


class TodayListItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    position = serializers.CharField(allow_null=True)
    record_type = serializers.CharField()


class WeeklyRateSerializer(serializers.Serializer):
    monday = serializers.FloatField(allow_null=True)
    tuesday = serializers.FloatField(allow_null=True)
    wednesday = serializers.FloatField(allow_null=True)
    thursday = serializers.FloatField(allow_null=True)
    friday = serializers.FloatField(allow_null=True)


class TodaySummarySerializer(serializers.Serializer):
    todays_records = TodayCountsSerializer()
    today_list = TodayListItemSerializer(many=True)
    weekly_rate = WeeklyRateSerializer()
