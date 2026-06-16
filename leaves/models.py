from django.db import models
from accounts.models import CustomUser, Grade


class LeaveType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class LeaveGradeDays(models.Model):
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE,
        related_name='grade_days'
    )
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE
    )
    days = models.IntegerField(default=0)

    class Meta:
        unique_together = ['leave_type', 'grade']

    def __str__(self):
        return f"{self.leave_type.name} - {self.grade.name}: {self.days} days"


class LeaveBalance(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE
    )
    total_days = models.IntegerField(default=0)
    used_days = models.IntegerField(default=0)
    year = models.IntegerField()

    @property
    def remaining_days(self):
        return self.total_days - self.used_days

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.leave_type.name} ({self.remaining_days} days left)"


class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Supervisor Review'),
        ('supervisor_approved', 'Approved by Supervisor'),
        ('supervisor_declined', 'Declined by Supervisor'),
        ('forwarded_to_hr', 'Forwarded to HR'),
        ('forwarded_to_approver', 'Forwarded to Approver'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    applicant = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='leave_applications'
    )
    chosen_supervisor = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='supervised_leaves'
    )
    chosen_approver = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_approvals'
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default='pending'
    )
    hr_comment = models.TextField(blank=True)
    supervisor_comment = models.TextField(blank=True)
    approver_comment = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.applicant.get_full_name()} - {self.leave_type.name} ({self.status})"