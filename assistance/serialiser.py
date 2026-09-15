from rest_framework import serializers

from .models import *
from accounts.permissions import is_admin_type

INGRESO_DELAY_THRESHOLD_HOUR = 9

class AssistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceRecord

        fields = [
            "id",
            "date",
            "time",
            "type",
            "user",
            "delay",
        ]
        read_only_fields = ["id","delay"]

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
        if validated_data.get("type") == AssistanceRecord.AssistanceType.INGRESO:
            validated_data["delay"] = validated_data["time"].hour >= INGRESO_DELAY_THRESHOLD_HOUR
        return super().create(validated_data)

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
