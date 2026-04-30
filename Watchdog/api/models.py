from django.db import models

# Create your models here.
class Monitor(models.Model):
    class STATUS(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        PAUSED = 'paused', 'Paused'
        
    id = models.CharField(max_length=255, primary_key=True)
    timeout = models.PositiveIntegerField(help_text="Timeout in seconds")
    alert_email = models.EmailField(help_text="Email to send alerts to")
    status = models.CharField(max_length=10, choices=STATUS.choices, default=STATUS.ACTIVE)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    last_checked = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)   
    
    def __str__(self):
        return f"Monitor {self.id} - Status: {self.status}"
    