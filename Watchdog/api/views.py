from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from celery import current_app
from .models import Monitor
from .tasks import fire_alert
from .serializers import MonitorSerializer

# Create your views here.
def schedule_alert(monitor):
    """Cancel any existing task and schedule a new one"""
    if monitor.celery_task_id:
        current_app.control.revoke(monitor.celery_task_id, terminate=True)
        
    task = fire_alert.apply_async(args=[monitor.id], countdown=monitor.timeout)
    monitor.celery_task_id = task.id
    monitor.expires_at = timezone.now() + timedelta(seconds=monitor.timeout)
    monitor.save(update_fields=['celery_task_id', 'expires_at'])
    
class MonitorListCreateView(APIView):
    def get(self, request):
        monitors = Monitor.objects.all().order_by("-created_at")
        return Response(MonitorSerializer(monitors, many=True).data)

    def post(self, request):
        serializer = MonitorSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        monitor = serializer.save(
            status=Monitor.STATUS.ACTIVE,
            expires_at=timezone.now() + timedelta(
                seconds=serializer.validated_data["timeout"]
            ),
        )
        schedule_alert(monitor)
        return Response(
            {"message": f"Monitor '{monitor.id}' registered.", "id": monitor.id},
            status=status.HTTP_201_CREATED,
        )


class MonitorDetailView(APIView):
    def _get(self, pk):
        try:
            return Monitor.objects.get(pk=pk)
        except Monitor.DoesNotExist:
            return None

    def get(self, request, pk):
        monitor = self._get(pk)
        if not monitor:
            return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(MonitorSerializer(monitor).data)


class HeartbeatView(APIView):
    def post(self, request, pk):
        try:
            monitor = Monitor.objects.get(pk=pk)
        except Monitor.DoesNotExist:
            return Response({"error": "Monitor not found."}, status=status.HTTP_404_NOT_FOUND)

        if monitor.status == Monitor.STATUS.INACTIVE:
            return Response(
                {"error": "Monitor is inactive. Re-register to restart."},
                status=status.HTTP_409_CONFLICT,
            )

        monitor.status = Monitor.STATUS.ACTIVE
        monitor.last_checked = timezone.now()
        monitor.save(update_fields=["status", "last_checked"])
        schedule_alert(monitor)  # resets the countdown

        return Response({"message": f"Heartbeat received. Timer reset to {monitor.timeout}s."})


class PauseView(APIView):
    def post(self, request, pk):
        try:
            monitor = Monitor.objects.get(pk=pk)
        except Monitor.DoesNotExist:
            return Response({"error": "Monitor not found."}, status=status.HTTP_404_NOT_FOUND)

        if monitor.status == Monitor.STATUS.PAUSED:
            return Response({"message": "Already paused."})

        if monitor.celery_task_id:
            current_app.control.revoke(monitor.celery_task_id, terminate=True)

        monitor.status = Monitor.STATUS.PAUSED
        monitor.celery_task_id = None
        monitor.save(update_fields=["status", "celery_task_id"])

        return Response({"message": f"Monitor '{pk}' paused. No alerts will fire."})


class ResumeView(APIView):
    def post(self, request, pk):
        try:
            monitor = Monitor.objects.get(pk=pk)
        except Monitor.DoesNotExist:
            return Response({"error": "Monitor not found."}, status=status.HTTP_404_NOT_FOUND)

        if monitor.status != Monitor.STATUS.PAUSED:
            return Response(
                {"error": f"Monitor is not paused (current status: '{monitor.status}')."},
                status=status.HTTP_409_CONFLICT,
            )

        monitor.status = Monitor.STATUS.ACTIVE
        monitor.last_checked = timezone.now()
        monitor.save(update_fields=["status", "last_checked"])
        schedule_alert(monitor)

        return Response({"message": f"Monitor '{pk}' resumed. Timer reset to {monitor.timeout}s."})