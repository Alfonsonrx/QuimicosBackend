from rest_framework import serializers
from .models import *

class AssistanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistanceRecord

        fields = [
            "id",
            "timestamp",
            "type",
            "user",
        ]
        read_only_fields = ["id"]
