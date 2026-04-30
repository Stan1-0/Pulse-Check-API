from rest_framework import serializers
from .models import Monitor
from django.utils import timezone

class MonitorSerializer(serializers.ModelSerializer):
    seconds_remaning = serializers.SerialzerMethodField()
    
    class Meta:
        model = Monitor
        fields = ["id", "timeout", "alert_email", "status", "last_heartbeat", "expires_at","created_at", "seconds_remaining"]
        read_only_fields = [ "status", "last_heartbeat", "expires_at", "created_at", ]
        
        def get_seconds_remaining(self, obj):
            if obj.status != Monitor.Status.ACTIVE:
                return None
            delta = (obj.expires_at - timezone.now()).total_seconds()
            return max(0, round(delta))
    