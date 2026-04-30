from celery import shared_task
from django.utils import timezone
import logging, json

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def fire_alert(self, monitor_id):
    from .models import Monitor
    try:
        monitor = Monitor.objects.get(pk=monitor_id)
    except Monitor.DoesNotExist:
        return f"Monitor with id {monitor_id} does not exist."
    
    if monitor.status != Monitor.STATUS.ACTIVE:
        return
    
    #only alert if still active
    monitor.status = Monitor.STATUS.INACTIVE
    monitor.save(update_fields=['status'])
    
    alert = {
        "Alert": f"Monitor {monitor_id} has timed out.",
        "time": timezone.now().isoformat(),
        "alert_email": monitor.alert_email
    }
    
    #loging the alert
    logger.critical(json.dumps(alert))
    print(json.dumps(alert))