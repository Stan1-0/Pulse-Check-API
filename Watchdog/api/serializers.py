from rest_framework import serializers
from .models import Monitor
from django.utils import timezone

class MonitorSerializer(serializers.ModelSerializer):
    seconds_remaining = serializers.SerializerMethodField()
    # Expose model field `last_checked` as `last_heartbeat` in API responses.
    last_heartbeat = serializers.DateTimeField(source="last_checked", read_only=True)
    
    class Meta:
        model = Monitor
        fields = [
            "id",
            "timeout",
            "alert_email",
            "seconds_remaining",
            "status",
            "last_heartbeat",
            "expires_at",
            "created_at",
        ]
        read_only_fields = ["status", "last_heartbeat", "expires_at", "created_at"]

    def get_seconds_remaining(self, obj):
        if obj.status != Monitor.STATUS.ACTIVE:
            return None
        delta = (obj.expires_at - timezone.now()).total_seconds()
        return max(0, round(delta))
    