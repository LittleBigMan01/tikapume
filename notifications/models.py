from django.db import models
from accounts.models import CustomUser
from leaves.models import LeaveApplication

class Notification(models.Model):
    TYPE_CHOICES = [
        ('leave_request', 'Leave Request'),
        ('leave_forwarded', 'Leave Forwarded'),
        ('leave_approved', 'Leave Approved'),
        ('leave_declined', 'Leave Declined'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications')
    leave_application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To: {self.recipient.get_full_name()} - {self.notification_type}"